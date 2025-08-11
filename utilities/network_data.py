#!/usr/bin/env python3
"""
Network Raw Data Utilities

This module provides utilities for parsing, analyzing, and manipulating
network raw data. Useful for network debugging, packet analysis, and
protocol development.
"""

import struct
import socket
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class EtherType(Enum):
    """Common Ethernet frame types"""
    IPV4 = 0x0800
    ARP = 0x0806
    IPV6 = 0x86DD
    VLAN = 0x8100


class IPProtocol(Enum):
    """Common IP protocol numbers"""
    ICMP = 1
    TCP = 6
    UDP = 17
    IPV6 = 41
    ICMPV6 = 58


@dataclass
class EthernetHeader:
    """Ethernet frame header"""
    dst_mac: str
    src_mac: str
    ethertype: int
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'EthernetHeader':
        """Parse Ethernet header from raw bytes"""
        if len(data) < 14:
            raise ValueError("Insufficient data for Ethernet header")
        
        dst_mac = ':'.join(f'{b:02x}' for b in data[0:6])
        src_mac = ':'.join(f'{b:02x}' for b in data[6:12])
        ethertype = struct.unpack('!H', data[12:14])[0]
        
        return cls(dst_mac, src_mac, ethertype)


@dataclass
class IPv4Header:
    """IPv4 packet header"""
    version: int
    ihl: int  # Internet Header Length
    tos: int  # Type of Service
    total_length: int
    identification: int
    flags: int
    fragment_offset: int
    ttl: int
    protocol: int
    checksum: int
    src_ip: str
    dst_ip: str
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'IPv4Header':
        """Parse IPv4 header from raw bytes"""
        if len(data) < 20:
            raise ValueError("Insufficient data for IPv4 header")
        
        # Unpack the first 20 bytes of IPv4 header
        fields = struct.unpack('!BBHHHBBH4s4s', data[0:20])
        
        version_ihl = fields[0]
        version = (version_ihl >> 4) & 0xF
        ihl = version_ihl & 0xF
        
        tos = fields[1]
        total_length = fields[2]
        identification = fields[3]
        flags_fragment = fields[4]
        flags = (flags_fragment >> 13) & 0x7
        fragment_offset = flags_fragment & 0x1FFF
        ttl = fields[5]
        protocol = fields[6]
        checksum = fields[7]
        src_ip = socket.inet_ntoa(fields[8])
        dst_ip = socket.inet_ntoa(fields[9])
        
        return cls(version, ihl, tos, total_length, identification,
                   flags, fragment_offset, ttl, protocol, checksum,
                   src_ip, dst_ip)


@dataclass
class TCPHeader:
    """TCP segment header"""
    src_port: int
    dst_port: int
    seq_num: int
    ack_num: int
    data_offset: int
    flags: int
    window_size: int
    checksum: int
    urgent_pointer: int
    
    @property
    def flag_names(self) -> List[str]:
        """Get human-readable flag names"""
        flag_list = []
        if self.flags & 0x01:
            flag_list.append("FIN")
        if self.flags & 0x02:
            flag_list.append("SYN")
        if self.flags & 0x04:
            flag_list.append("RST")
        if self.flags & 0x08:
            flag_list.append("PSH")
        if self.flags & 0x10:
            flag_list.append("ACK")
        if self.flags & 0x20:
            flag_list.append("URG")
        if self.flags & 0x40:
            flag_list.append("ECE")
        if self.flags & 0x80:
            flag_list.append("CWR")
        return flag_list
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'TCPHeader':
        """Parse TCP header from raw bytes"""
        if len(data) < 20:
            raise ValueError("Insufficient data for TCP header")
        
        fields = struct.unpack('!HHLLBBHHH', data[0:20])
        
        src_port = fields[0]
        dst_port = fields[1]
        seq_num = fields[2]
        ack_num = fields[3]
        data_offset_flags = fields[4]
        data_offset = (data_offset_flags >> 4) & 0xF
        flags = fields[5]
        window_size = fields[6]
        checksum = fields[7]
        urgent_pointer = fields[8]
        
        return cls(src_port, dst_port, seq_num, ack_num, data_offset,
                   flags, window_size, checksum, urgent_pointer)


@dataclass
class UDPHeader:
    """UDP datagram header"""
    src_port: int
    dst_port: int
    length: int
    checksum: int
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'UDPHeader':
        """Parse UDP header from raw bytes"""
        if len(data) < 8:
            raise ValueError("Insufficient data for UDP header")
        
        fields = struct.unpack('!HHHH', data[0:8])
        return cls(fields[0], fields[1], fields[2], fields[3])


class NetworkPacketParser:
    """Parser for network packets from raw data"""
    
    def __init__(self):
        self.ethernet_header: Optional[EthernetHeader] = None
        self.ipv4_header: Optional[IPv4Header] = None
        self.tcp_header: Optional[TCPHeader] = None
        self.udp_header: Optional[UDPHeader] = None
        self.payload: bytes = b''
    
    def parse_ethernet_frame(self, data: bytes) -> int:
        """Parse Ethernet frame and return offset to next layer"""
        self.ethernet_header = EthernetHeader.from_bytes(data)
        return 14  # Ethernet header is always 14 bytes
    
    def parse_ipv4_packet(self, data: bytes, offset: int = 0) -> int:
        """Parse IPv4 packet and return offset to next layer"""
        self.ipv4_header = IPv4Header.from_bytes(data[offset:])
        header_length = self.ipv4_header.ihl * 4
        return offset + header_length
    
    def parse_tcp_segment(self, data: bytes, offset: int = 0) -> int:
        """Parse TCP segment and return offset to payload"""
        self.tcp_header = TCPHeader.from_bytes(data[offset:])
        header_length = self.tcp_header.data_offset * 4
        return offset + header_length
    
    def parse_udp_datagram(self, data: bytes, offset: int = 0) -> int:
        """Parse UDP datagram and return offset to payload"""
        self.udp_header = UDPHeader.from_bytes(data[offset:])
        return offset + 8  # UDP header is always 8 bytes
    
    def parse_packet(self, data: bytes, has_ethernet: bool = True) -> Dict:
        """Parse complete packet and return summary"""
        offset = 0
        
        # Parse Ethernet layer
        if has_ethernet:
            offset = self.parse_ethernet_frame(data)
            
            # Check if this is an IP packet
            if self.ethernet_header.ethertype != EtherType.IPV4.value:
                ethertype_hex = f"0x{self.ethernet_header.ethertype:04x}"
                return {"error": f"Unsupported EtherType: {ethertype_hex}"}
        
        # Parse IP layer
        if len(data) > offset:
            offset = self.parse_ipv4_packet(data, offset)
            
            # Parse transport layer
            if self.ipv4_header.protocol == IPProtocol.TCP.value:
                offset = self.parse_tcp_segment(data, offset)
            elif self.ipv4_header.protocol == IPProtocol.UDP.value:
                offset = self.parse_udp_datagram(data, offset)
        
        # Extract payload
        if len(data) > offset:
            self.payload = data[offset:]
        
        return self.get_summary()
    
    def get_summary(self) -> Dict:
        """Get a summary of the parsed packet"""
        summary = {}
        
        if self.ethernet_header:
            summary['ethernet'] = {
                'src_mac': self.ethernet_header.src_mac,
                'dst_mac': self.ethernet_header.dst_mac,
                'ethertype': f"0x{self.ethernet_header.ethertype:04x}"
            }
        
        if self.ipv4_header:
            summary['ipv4'] = {
                'src_ip': self.ipv4_header.src_ip,
                'dst_ip': self.ipv4_header.dst_ip,
                'protocol': self.ipv4_header.protocol,
                'ttl': self.ipv4_header.ttl,
                'total_length': self.ipv4_header.total_length
            }
        
        if self.tcp_header:
            summary['tcp'] = {
                'src_port': self.tcp_header.src_port,
                'dst_port': self.tcp_header.dst_port,
                'seq_num': self.tcp_header.seq_num,
                'ack_num': self.tcp_header.ack_num,
                'flags': self.tcp_header.flag_names,
                'window_size': self.tcp_header.window_size
            }
        
        if self.udp_header:
            summary['udp'] = {
                'src_port': self.udp_header.src_port,
                'dst_port': self.udp_header.dst_port,
                'length': self.udp_header.length
            }
        
        if self.payload:
            preview = self.payload[:32].hex() if len(self.payload) > 0 else ""
            summary['payload'] = {
                'length': len(self.payload),
                'data_preview': preview
            }
        
        return summary


class NetworkDataUtils:
    """Utility functions for network data manipulation"""
    
    @staticmethod
    def hex_dump(data: bytes, width: int = 16, show_ascii: bool = True) -> str:
        """Create a hex dump of binary data"""
        lines = []
        for i in range(0, len(data), width):
            chunk = data[i:i + width]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            hex_part = hex_part.ljust(width * 3 - 1)
            
            if show_ascii:
                ascii_chars = [chr(b) if 32 <= b <= 126 else '.'
                               for b in chunk]
                ascii_part = ''.join(ascii_chars)
                lines.append(f'{i:08x}  {hex_part}  |{ascii_part}|')
            else:
                lines.append(f'{i:08x}  {hex_part}')
        
        return '\n'.join(lines)
    
    @staticmethod
    def calculate_ip_checksum(data: bytes) -> int:
        """Calculate IPv4 header checksum"""
        # Make sure data length is even
        if len(data) % 2:
            data += b'\x00'
        
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
        
        # Add carry
        while checksum >> 16:
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        
        return (~checksum) & 0xFFFF
    
    @staticmethod
    def mac_to_bytes(mac_str: str) -> bytes:
        """Convert MAC address string to bytes"""
        return bytes.fromhex(mac_str.replace(':', ''))
    
    @staticmethod
    def bytes_to_mac(mac_bytes: bytes) -> str:
        """Convert MAC address bytes to string"""
        return ':'.join(f'{b:02x}' for b in mac_bytes)
    
    @staticmethod
    def ip_to_bytes(ip_str: str) -> bytes:
        """Convert IP address string to bytes"""
        return socket.inet_aton(ip_str)
    
    @staticmethod
    def bytes_to_ip(ip_bytes: bytes) -> str:
        """Convert IP address bytes to string"""
        return socket.inet_ntoa(ip_bytes)


def example_usage():
    """Example usage of the network data utilities"""
    print("Network Raw Data Utilities - Example Usage")
    print("=" * 50)
    
    # Example: Create a simple Ethernet + IP + TCP packet
    # This is for demonstration - normally from pcap or network capture
    
    # Example raw packet data (simplified)
    sample_data = bytes.fromhex(
        # Ethernet header (14 bytes)
        "001122334455"  # dst MAC
        "aabbccddeeff"  # src MAC
        "0800"          # EtherType (IPv4)
        # IPv4 header (20 bytes)
        "45"            # Version (4) + IHL (5)
        "00"            # TOS
        "003c"          # Total Length
        "1234"          # Identification
        "4000"          # Flags + Fragment Offset
        "40"            # TTL
        "06"            # Protocol (TCP)
        "0000"          # Checksum (placeholder)
        "c0a80101"      # Source IP (192.168.1.1)
        "c0a80102"      # Dest IP (192.168.1.2)
        # TCP header (20 bytes)
        "0050"          # Source Port (80)
        "1234"          # Dest Port (4660)
        "12345678"      # Sequence Number
        "87654321"      # Acknowledgment Number
        "50"            # Data Offset (5 words = 20 bytes)
        "18"            # Flags (PSH + ACK)
        "2000"          # Window Size
        "0000"          # Checksum (placeholder)
        "0000"          # Urgent Pointer
        # Payload
        "48656c6c6f20576f726c64"  # "Hello World"
    )
    
    # Parse the packet
    parser = NetworkPacketParser()
    summary = parser.parse_packet(sample_data)
    
    print("Packet Summary:")
    for layer, info in summary.items():
        print(f"\n{layer.upper()}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    print("\nHex Dump:")
    print(NetworkDataUtils.hex_dump(sample_data))


if __name__ == "__main__":
    example_usage()
