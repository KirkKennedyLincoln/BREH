import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def load_all() -> pd.DataFrame:
    files = {
        "CONTROL":   "./data/training/controlnet_latency_data_anon.csv",
        "LORA":      "./data/training/lora_update_latency_anon.csv",
        "MODEL":     "./data/training/model_predict_data_anon.csv",
        "PIPELINE":  "./data/training/basemodel_update_latency_anon.csv",
        "DUTY":      "./data/training/pod_gpu_duty_cycle_anon.csv",
        "BYTES":     "./data/training/pod_gpu_memory_used_bytes_anon.csv",
        "INFERENCE": "./data/training/pipeline_inference_data_anon.csv",
        "UTIL":      "./data/training/pod_memory_util_anon.csv",
        "QPS":       "./data/training/qps.csv",
        "QUEUE_SIZE": "./data/training/queue_size_raw_anon.csv",
        "QUEUE_RT":  "./data/training/queue_rt_raw_anon.csv",
    }
    dfs = []
    for metric, path in files.items():
        df = pd.read_csv(path)
        df["metric"] = metric
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def prepare(merged: pd.DataFrame) -> pd.DataFrame:
    # 5-minute time bins
    merged["time_bin"] = (merged["timestamp_anon"] // 300) * 300

    # long -> wide: one column per metric, one row per (container, time_bin)
    wide = merged.pivot_table(
        index=["container_ip", "time_bin"],
        columns="metric",
        values="value",
        aggfunc="mean",
    ).reset_index()

    # target: 1 if this bin's mean queue size exceeds the 70th percentile
    qs_by_time = merged[merged["metric"] == "QUEUE_SIZE"].groupby("time_bin")["value"].mean()
    threshold = qs_by_time.quantile(0.75)
    wide["needs_scale_up"] = (
        wide["time_bin"].map(qs_by_time > threshold).fillna(False).astype(int)
    )

    # drop UTIL (mostly NaN) and QUEUE_SIZE (was the target)
    wide = wide.drop(columns=["UTIL", "QUEUE_SIZE"], errors="ignore")

    feature_cols = ["BYTES", "CONTROL", "DUTY", "INFERENCE",
                    "LORA", "MODEL", "PIPELINE", "QPS", "QUEUE_RT"]
    for col in feature_cols:
        if col in wide.columns:
            wide[col] = wide.groupby("time_bin")[col].transform(lambda x: x.fillna(x.mean()))

    return wide.dropna()


def main() -> None:
    print("loading...")
    merged = load_all()
    wide = prepare(merged)
    print(f"prepared: {wide.shape}")

    X = wide.drop(columns=["container_ip", "time_bin", "needs_scale_up"])
    y = wide["needs_scale_up"]
    feature_names = list(X.columns)
    print(f"features: {feature_names}")
    print(f"class balance:\n{y.value_counts()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    clf = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
    clf.fit(X_train_scaled, y_train)
    print(f"train acc: {clf.score(X_train_scaled, y_train):.4f}")
    print(f"test acc:  {clf.score(X_test_scaled, y_test):.4f}")

    joblib.dump(clf, "models/scaling_classifier.pkl")
    joblib.dump(scaler, "models/scaling_scaler.pkl")
    joblib.dump(feature_names, "models/scaling_features.pkl")
    print("dumped: scaling_classifier.pkl, scaling_scaler.pkl, scaling_features.pkl")


if __name__ == "__main__":
    main()
