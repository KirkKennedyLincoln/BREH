package runner

import (
	"bytes"
	"context"
	"io"

	"github.com/KirkKennedyLincoln/BREH/gen/runnerpb"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/image"
	"github.com/docker/docker/api/types/mount"
	"github.com/docker/docker/api/types/strslice"
	"github.com/docker/docker/client"
	"github.com/docker/docker/pkg/stdcopy"
	"github.com/docker/go-connections/nat"
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

func (d *Docker) Spawn(ctx context.Context, req *runnerpb.SpawnRequest) (*runnerpb.SpawnResponse, error) {
	cfg := &container.Config{
		Image: req.ImageName,
		Cmd:   req.Cmd,
		Env:   req.Env,
	}

	hostCfg := &container.HostConfig{
		Binds:           []string{},
		ContainerIDFile: "",
		LogConfig:       container.LogConfig{},
		NetworkMode:     "",
		PortBindings:    nat.PortMap{},
		RestartPolicy:   container.RestartPolicy{},
		AutoRemove:      false,
		VolumeDriver:    "",
		VolumesFrom:     []string{},
		ConsoleSize:     [2]uint{},
		Annotations:     map[string]string{},
		CapAdd:          strslice.StrSlice{},
		CapDrop:         strslice.StrSlice{},
		CgroupnsMode:    "",
		DNS:             []string{},
		DNSOptions:      []string{},
		DNSSearch:       []string{},
		ExtraHosts:      []string{},
		GroupAdd:        []string{},
		IpcMode:         "",
		Cgroup:          "",
		Links:           []string{},
		OomScoreAdj:     0,
		PidMode:         "",
		Privileged:      false,
		PublishAllPorts: false,
		ReadonlyRootfs:  false,
		SecurityOpt:     []string{},
		StorageOpt:      map[string]string{},
		Tmpfs:           map[string]string{},
		UTSMode:         "",
		UsernsMode:      "",
		ShmSize:         0,
		Sysctls:         map[string]string{},
		Runtime:         "",
		Isolation:       "",
		Resources:       container.Resources{},
		Mounts:          []mount.Mount{},
		MaskedPaths:     []string{},
		ReadonlyPaths:   []string{},
		Init:            new(bool),
	}

	resp, err := d.cli.ContainerCreate(ctx, cfg, hostCfg, nil, nil, "")
	if err != nil {
		return nil, nil
	}

	d.cli.ContainerStart(ctx, resp.ID, container.StartOptions{})
	return &runnerpb.SpawnResponse{
		Id: resp.ID,
	}, nil
}

func (d *Docker) Wait(ctx context.Context, req *runnerpb.WaitRequest) (*runnerpb.WaitResponse, error) {
	var exitCode int64
	statusCh, errCh := d.cli.ContainerWait(ctx, req.Id, container.WaitConditionNotRunning)

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
