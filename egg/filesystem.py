from enum import Enum


class Filesystem(Enum):
    NTFS = 'ntfs'
    EXT4 = 'ext4'
    FAT32 = 'fat32'
    SWAP = 'swap'
    UNKNOWN = 'unknown'
    NOT_ALLOCATED = 'notallocated'
