from typing import List

import pytest
from grpclib.testing import ChannelFor

from viam.proto.common import DoCommandRequest, DoCommandResponse
from viam.proto.service.slam import (
    GetInternalStateRequest,
    GetInternalStateResponse,
    GetLatestMapInfoRequest,
    GetLatestMapInfoResponse,
    GetPointCloudMapRequest,
    GetPointCloudMapResponse,
    GetPositionRequest,
    GetPositionResponse,
    SLAMServiceStub,
)
from viam.resource.manager import ResourceManager
from viam.services.slam import SLAMClient, SLAMRPCService
from viam.utils import dict_to_struct, struct_to_dict

from .mocks.services import MockSLAM


class TestSLAMService:
    name = "slam"
    slam = MockSLAM(name="slam")

    @pytest.mark.asyncio
    async def test_get_internal_state_chunks(self):
        chunks = await self.slam.get_internal_state()
        assert chunks == MockSLAM.INTERNAL_STATE_CHUNKS

    @pytest.mark.asyncio
    async def test_get_point_cloud_map(self):
        chunks = await self.slam.get_point_cloud_map()
        assert chunks == MockSLAM.POINT_CLOUD_PCD_CHUNKS

    @pytest.mark.asyncio
    async def test_get_position(self):
        pos = await self.slam.get_position()
        assert pos == MockSLAM.POSITION

    @pytest.mark.asyncio
    async def test_get_latest_map_info(self):
        time = await self.slam.get_latest_map_info()
        assert time == MockSLAM.LAST_UPDATE

    @pytest.mark.asyncio
    async def test_do(self):
        command = {"command": "args"}
        resp = await self.slam.do_command(command)
        assert resp == {"command": command}


class TestService:
    @classmethod
    def setup_class(cls):
        cls.name = "slam"
        cls.slam = MockSLAM(name=cls.name)
        cls.manager = ResourceManager([cls.slam])
        cls.service = SLAMRPCService(cls.manager)

    @pytest.mark.asyncio
    async def test_get_internal_state(self):
        async with ChannelFor([self.service]) as channel:
            client = SLAMServiceStub(channel)
            request = GetInternalStateRequest(name=self.name)
            response: List[GetInternalStateResponse] = await client.GetInternalState(request)
            for i, chunk in enumerate(response):
                assert chunk.internal_state_chunk == MockSLAM.INTERNAL_STATE_CHUNKS[i]

    @pytest.mark.asyncio
    async def test_get_point_cloud_map(self):
        async with ChannelFor([self.service]) as channel:
            client = SLAMServiceStub(channel)
            request = GetPointCloudMapRequest(name=self.name)
            response: List[GetPointCloudMapResponse] = await client.GetPointCloudMap(request)
            for i, chunk in enumerate(response):
                assert chunk.point_cloud_pcd_chunk == MockSLAM.POINT_CLOUD_PCD_CHUNKS[i]

    @pytest.mark.asyncio
    async def test_get_position(self):
        async with ChannelFor([self.service]) as channel:
            client = SLAMServiceStub(channel)
            request = GetPositionRequest(name=self.name)
            response: GetPositionResponse = await client.GetPosition(request)
            assert response.pose == MockSLAM.POSITION

    @pytest.mark.asyncio
    async def test_get_latest_map_info(self):
        async with ChannelFor([self.service]) as channel:
            client = SLAMServiceStub(channel)
            request = GetLatestMapInfoRequest(name=self.name)
            response: GetLatestMapInfoResponse = await client.GetLatestMapInfo(request)
            assert response.last_map_update.ToDatetime() == MockSLAM.LAST_UPDATE

    @pytest.mark.asyncio
    async def test_do(self):
        async with ChannelFor([self.service]) as channel:
            client = SLAMServiceStub(channel)
            command = {"command": "args"}
            request = DoCommandRequest(name=self.name, command=dict_to_struct(command))
            response: DoCommandResponse = await client.DoCommand(request)
            result = struct_to_dict(response.result)
            assert result == {"command": command}


class TestClient:
    @classmethod
    def setup_class(cls):
        cls.name = "slam"
        cls.slam = MockSLAM(name=cls.name)
        cls.manager = ResourceManager([cls.slam])
        cls.service = SLAMRPCService(cls.manager)

    @pytest.mark.asyncio
    async def test_get_internal_state(self):
        async with ChannelFor([self.service]) as channel:
            client = SLAMClient(self.name, channel)
            response = await client.get_internal_state()
            assert len(response) == len(MockSLAM.INTERNAL_STATE_CHUNKS)
            for i, chunk in enumerate(response):
                assert chunk.internal_state_chunk == MockSLAM.INTERNAL_STATE_CHUNKS[i]

    @pytest.mark.asyncio
    async def test_get_point_cloud_map(self):
        async with ChannelFor([self.service]) as channel:
            client = SLAMClient(self.name, channel)
            response = await client.get_point_cloud_map()
            assert len(response) == len(MockSLAM.POINT_CLOUD_PCD_CHUNKS)
            for i, chunk in enumerate(response):
                assert chunk.point_cloud_pcd_chunk == MockSLAM.POINT_CLOUD_PCD_CHUNKS[i]

    @pytest.mark.asyncio
    async def test_get_position(self):
        async with ChannelFor([self.service]) as channel:
            client = SLAMClient(self.name, channel)
            response = await client.get_position()
            assert response == MockSLAM.POSITION

    @pytest.mark.asyncio
    async def test_get_latest_map_info(self):
        async with ChannelFor([self.service]) as channel:
            client = SLAMClient(self.name, channel)
            response = await client.get_latest_map_info()
            assert response == MockSLAM.LAST_UPDATE

    @pytest.mark.asyncio
    async def test_do(self):
        async with ChannelFor([self.service]) as channel:
            client = SLAMClient(self.name, channel)
            command = {"command": "args"}
            response = await client.do_command(command)
            assert response == {"command": command}
