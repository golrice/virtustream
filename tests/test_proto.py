import pytest
import struct
from unittest.mock import patch
from proto import Proto

def test_proto_unpack_valid_packet():
    """测试正常数据包的解包"""
    proto = Proto()
    
    # 构造一个有效的数据包
    packet_len = 20  # 16字节头部 + 4字节body
    header_len = 16
    ver = 0
    op = 1
    seq = 123
    body = "test"
    
    # 手动构造二进制数据包
    buf = struct.pack('>i', packet_len)  # packetLen
    buf += struct.pack('>h', header_len)  # headerLen
    buf += struct.pack('>h', ver)  # ver
    buf += struct.pack('>i', op)  # op
    buf += struct.pack('>i', seq)  # seq
    buf += body.encode()  # body
    
    # 使用patch捕获print输出
    with patch('builtins.print') as mock_print:
        proto.unpack(buf)
        
    # 验证解包结果
    assert proto.packetLen == packet_len
    assert proto.headerLen == header_len
    assert proto.ver == ver
    assert proto.op == op
    assert proto.seq == seq
    assert proto.body == body.encode()
    
    # 验证回调被调用
    mock_print.assert_called_with("====> callback:", body)

def test_proto_unpack_insufficient_header():
    """测试包头长度不足的情况"""
    proto = Proto()
    
    # 构造一个长度不足的数据包（少于16字节）
    buf = b'short'
    
    with patch('builtins.print') as mock_print:
        proto.unpack(buf)
        
    # 验证错误信息被打印
    mock_print.assert_called_with("包头不够")

def test_proto_unpack_invalid_packet_length():
    """测试无效包长度的情况"""
    proto = Proto()
    
    # 构造一个包长度超出限制的数据包
    packet_len = 3000  # 超过maxBody(2048)
    header_len = 16
    ver = 0
    op = 1
    seq = 123
    
    buf = struct.pack('>i', packet_len)
    buf += struct.pack('>h', header_len)
    buf += struct.pack('>h', ver)
    buf += struct.pack('>i', op)
    buf += struct.pack('>i', seq)
    
    with patch('builtins.print') as mock_print:
        proto.unpack(buf)
        
    # 验证错误信息被打印
    mock_print.assert_called_with("包体长不对", "self.packetLen:", packet_len, " self.maxBody:", 2048)

def test_proto_unpack_negative_packet_length():
    """测试负数包长度的情况"""
    proto = Proto()
    
    # 构造一个负数包长度的数据包
    packet_len = -1
    header_len = 16
    ver = 0
    op = 1
    seq = 123
    
    buf = struct.pack('>i', packet_len)
    buf += struct.pack('>h', header_len)
    buf += struct.pack('>h', ver)
    buf += struct.pack('>i', op)
    buf += struct.pack('>i', seq)
    
    with patch('builtins.print') as mock_print:
        proto.unpack(buf)
        
    # 验证错误信息被打印
    mock_print.assert_called_with("包体长不对", "self.packetLen:", packet_len, " self.maxBody:", 2048)

def test_proto_unpack_empty_body():
    """测试空body的情况"""
    proto = Proto()
    
    # 构造一个只有头部没有body的数据包
    packet_len = 16  # 只有头部
    header_len = 16
    ver = 0
    op = 1
    seq = 123
    
    buf = struct.pack('>i', packet_len)
    buf += struct.pack('>h', header_len)
    buf += struct.pack('>h', ver)
    buf += struct.pack('>i', op)
    buf += struct.pack('>i', seq)
    
    proto.unpack(buf)
    
    # 验证解包结果
    assert proto.packetLen == packet_len
    assert proto.headerLen == header_len
    assert proto.ver == ver
    assert proto.op == op
    assert proto.seq == seq
    assert proto.body == b''  # 空body

def test_proto_unpack_version_not_zero():
    """测试版本号不为0的情况"""
    proto = Proto()
    
    # 构造一个版本号不为0的数据包
    packet_len = 20
    header_len = 16
    ver = 1  # 非0版本
    op = 1
    seq = 123
    body = "test"
    
    buf = struct.pack('>i', packet_len)
    buf += struct.pack('>h', header_len)
    buf += struct.pack('>h', ver)
    buf += struct.pack('>i', op)
    buf += struct.pack('>i', seq)
    buf += body.encode()
    
    with patch('builtins.print') as mock_print:
        proto.unpack(buf)
        
    # 验证解包成功但不会调用回调
    assert proto.packetLen == packet_len
    assert proto.ver == ver
    # 验证没有打印回调信息
    mock_print.assert_not_called()
