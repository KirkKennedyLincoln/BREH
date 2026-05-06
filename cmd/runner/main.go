package main

import (
	"log"
	"net"

	"github.com/KirkKennedyLincoln/BREH/gen/runnerpb"
	"github.com/KirkKennedyLincoln/BREH/internal/runner"
	"google.golang.org/grpc"
)

func main() {
	docker := runner.New()
	grpcServer := grpc.NewServer()
	runnerpb.RegisterRunnerServer(grpcServer, docker)

	lis, err := net.Listen("tcp", ":50055")
	if err != nil {
		log.Fatal(err.Error())
	}
	log.Println("runner server on :50055")
	log.Fatal(grpcServer.Serve(lis))
}
