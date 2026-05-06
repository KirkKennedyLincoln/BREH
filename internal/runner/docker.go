package runner

import (
	"bytes"
	"context"
	"io"

	"github.com/KirkKennedyLincoln/BREH/gen/runnerpb"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/image"
	"github.com/docker/docker/api/types/strslice"
	"github.com/docker/docker/client"
	"github.com/docker/docker/pkg/stdcopy"
)

type Docker struct {
	runnerpb.UnimplementedRunnerServer
	cli *client.Client
}

func New() *Docker {
	newClient, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return nil
	}

	return &Docker{
		cli: newClient,
	}
}

func (d *Docker) Close() error {
	return d.cli.Close()
}

func ptrBool(arg bool) *bool {
	return &arg
}

func ptrInt64(i int64) *int64 {
	return &i
}

func (d *Docker) Socket() {
	
}

func (d *Docker) Spawn(ctx context.Context, req *runnerpb.SpawnRequest) (*runnerpb.SpawnResponse, error) {
	cfg := &container.Config{
		Image: req.ImageName,
		Cmd:   req.Cmd,
		Env:   req.Env,
	}

	hostCfg := &container.HostConfig{
		// one-shot lifecycle
		AutoRemove: false,
		RestartPolicy: container.RestartPolicy{
			Name: "no",
		},
		Init: ptrBool(true),

		// resource caps -> prevents agent from running away with memory usage
		Resources: container.Resources{
			NanoCPUs:   1_000_000_000,     // 1 CPU
			Memory:     512 * 1024 * 1024, // 512MiB
			MemorySwap: 512 * 1024 * 1024, // 512 MiB
			PidsLimit:  ptrInt64(256),     // prevent DDOS'ing myself
		},

		// hardening for external LLM usage
		ReadonlyRootfs: true,
		CapDrop:        strslice.StrSlice{"ALL"},
		SecurityOpt:    []string{"no-new-privileges:true"},
		// host-gateway resolves to the host on Linux; harmless on Mac/Windows
		// where Docker Desktop already injects host.docker.internal.
		ExtraHosts: []string{"host.docker.internal:host-gateway"},

		// logging -> bound disk usage for chatty agents
		LogConfig: container.LogConfig{
			Type:   "json-file",
			Config: map[string]string{"max-size": "10m", "max-file": "3"},
		},
	}

	resp, err := d.cli.ContainerCreate(ctx, cfg, hostCfg, nil, nil, "")
	if err != nil {
		return nil, err
	}

	if err := d.cli.ContainerStart(ctx, resp.ID, container.StartOptions{}); err != nil {
		return nil, err
	}
	return &runnerpb.SpawnResponse{
		Id: resp.ID,
	}, nil
}

func (d *Docker) Wait(ctx context.Context, req *runnerpb.WaitRequest) (*runnerpb.WaitResponse, error) {
	var exitCode int64
	statusCh, errCh := d.cli.ContainerWait(ctx, req.Id, container.WaitConditionNotRunning)

	// block on channels waiting for results
	select {
	case err := <-errCh:
		return nil, err
	case status := <-statusCh:
		exitCode = status.StatusCode
	}

	logs, err := d.cli.ContainerLogs(ctx, req.Id, container.LogsOptions{
		ShowStdout: true,
		ShowStderr: true,
	})
	if err != nil {
		return nil, err
	}
	defer logs.Close()

	var stdout, stderr bytes.Buffer
	stdcopy.StdCopy(&stdout, &stderr, logs)
	return &runnerpb.WaitResponse{
		ExitCode: float32(exitCode),
		Logs: map[string]string{
			"stdout": stdout.String(),
			"stderr": stderr.String(),
		},
	}, nil
}

func (d *Docker) Kill(ctx context.Context, req *runnerpb.KillRequest) (*runnerpb.KillResponse, error) {
	timeoutSec := 5
	if err := d.cli.ContainerStop(ctx, req.Id, container.StopOptions{Timeout: &timeoutSec}); err != nil {
		return nil, err
	}
	if err := d.cli.ContainerRemove(ctx, req.Id, container.RemoveOptions{Force: true}); err != nil {
		return nil, err
	}

	return &runnerpb.KillResponse{
		Success: true,
	}, nil
}

func (d *Docker) Pull(ctx context.Context, imageName string) error {
	rc, err := d.cli.ImagePull(ctx, imageName, image.PullOptions{})
	if err != nil {
		return err
	}

	defer rc.Close()
	io.Copy(io.Discard, rc)

	return nil
}
