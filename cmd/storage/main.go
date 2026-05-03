package main

import (
	"log"
	"net"

	"github.com/KirkKennedyLincoln/BREH/gen/storagepb"
	"github.com/KirkKennedyLincoln/BREH/internal/storage"

	clientv3 "go.etcd.io/etcd/client/v3"
	"google.golang.org/grpc"
)

func main() {
	etcdClient, err := clientv3.New(clientv3.Config{
		Endpoints: []string{"localhost:2379"},
	})
	if err != nil {
		log.Fatal("etcd connect failed:", err)
	}
	defer etcdClient.Close()

	store := storage.NewStore(etcdClient, "/graphs/")

	grpcServer := grpc.NewServer()
	storagepb.RegisterGraphStoreServer(grpcServer, store)

	lis, err := net.Listen("tcp", ":50054")
	if err != nil {
		log.Fatal("listen failed:", err)
	}

	log.Println("storage server on :50054")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatal("serve failed:", err)
	}
}
