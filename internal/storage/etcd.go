package storage

import (
	"context"
	"strings"

	"github.com/KirkKennedyLincoln/BREH/gen/storagepb"
	clientv3 "go.etcd.io/etcd/client/v3"
)

type Store struct {
	storagepb.UnimplementedGraphStoreServer
	client *clientv3.Client
	prefix string
}

func NewStore(client *clientv3.Client, prefix string) *Store {
	return &Store{
		client: client,
		prefix: prefix,
	}
}

func (s *Store) Put(ctx context.Context, req *storagepb.PutRequest) (*storagepb.PutResponse, error) {
	key := s.prefix + req.Graph.Id
	_, err := s.client.Put(ctx, key, req.Graph.Data)
	if err != nil {
		return &storagepb.PutResponse{Success: false}, err
	}
	return &storagepb.PutResponse{Success: true}, nil
}

func (s *Store) Get(ctx context.Context, req *storagepb.GetRequest) (*storagepb.GetResponse, error) {
	key := s.prefix + req.Id
	res, err := s.client.Get(ctx, key)
	if err != nil {
		return nil, err
	}
	if len(res.Kvs) == 0 {
		return &storagepb.GetResponse{}, nil
	}
	return &storagepb.GetResponse{
		Graph: &storagepb.Graph{
			Id:   req.Id,
			Data: string(res.Kvs[0].Value),
		},
	}, nil
}

func (s *Store) List(ctx context.Context, req *storagepb.ListRequest) (*storagepb.ListResponse, error) {
	prefix := s.prefix + req.Prefix
	res, err := s.client.Get(ctx, prefix, clientv3.WithPrefix())
	if err != nil {
		return nil, err
	}
	ids := make([]string, len(res.Kvs))
	for i, kv := range res.Kvs {
		after, _ := strings.CutPrefix(string(kv.Key), "/graphs/")
		ids[i] = after
	}
	return &storagepb.ListResponse{Ids: ids}, nil
}

func (s *Store) Delete(ctx context.Context, req *storagepb.DeleteRequest) (*storagepb.DeleteResponse, error) {
	key := s.prefix + req.Id
	_, err := s.client.Delete(ctx, key)
	if err != nil {
		return &storagepb.DeleteResponse{Success: false}, err
	}
	return &storagepb.DeleteResponse{Success: true}, nil
}
