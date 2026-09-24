first_output = """
Error: /dev/sda: unrecognised disk label
Model: ATA mSATA 3SE4 (scsi)
Disk /dev/sda: 8012MB
Sector size (logical/physical): 512B/512B
Partition Table: unknown
Disk Flags: 

Model: ATA VBOX HARDDISK (scsi)
Disk /dev/sdb: 20.0GB
Sector size (logical/physical): 512B/512B
Partition Table: msdos
Disk Flags: 

Number  Start   End     Size    Type     File system  Flags
 1      1049kB  20.0GB  20.0GB  primary  ext4         boot

Model: ATA VBOX HARDDISK (scsi)
Disk /dev/sdc: 50.0GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: 

Number  Start   End     Size    File system  Name  Flags
 1      1049kB  50.0GB  50.0GB  ext4         primary
 2      50.0GB  50.0GB  512MB   swap

Model: ATA VBOX HARDDISK (scsi)
Disk /dev/sdd: 100.0GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: 

Number  Start   End     Size    File system  Name  Flags
 1      1049kB  50.0GB  50.0GB  ext4         primary
 2      50.0GB  100.0GB  50.0GB  ext4         primary
"""


sda = """
/dev/sda:
 Model=ATA mSATA 3SE4, FwRev=1.0, SerialNo=1234567890
 Config={ HardSect NotMFM HideSecRot }
 RawCHS=16383/16/63, TrkSize=63, SectSize=512
 Transport=ATA, SFF=0x3, SATAPI=0
"""


sdb = """
/dev/sdb:
 Model=ATA VBOX HARDDISK, FwRev=1.0, SerialNo=9876543210
 Config={ HardSect NotMFM HideSecRot }
 RawCHS=16383/16/63, TrkSize=63, SectSize=512
 Transport=ATA, SFF=0x3, SATAPI=0
"""

sdc = """
/dev/sdc:
 Model=ATA VBOX HARDDISK, FwRev=1.0, SerialNo=1122334455
 Config={ HardSect NotMFM HideSecRot }
 RawCHS=16383/16/63, TrkSize=63, SectSize=512
 Transport=ATA, SFF=0x3, SATAPI=0
"""

sdd = """
/dev/sdd:
 Model=ATA VBOX HARDDISK, FwRev=1.0, SerialNo=5566778899
 Config={ HardSect NotMFM HideSecRot }
 RawCHS=16383/16/63, TrkSize=63, SectSize=512
 Transport=ATA, SFF=0x3, SATAPI=0
"""

sdb_2 = """
/dev/sdb:
 Model=InnoDisk Corp. - mSATA 3SE3, FwRev=S17411, SerialNo=YCA11903250110014
 Config={ Fixed }
 RawCHS=15525/16/63, TrkSize=0, SectSize=0, ECCbytes=0
 BuffType=unknown, BuffSize=unknown, MaxMultSect=1, MultSect=1
 CurCHS=15525/16/63, CurSects=15649200, LBA=yes, LBAsects=15649200
 IORDY=on/off, tPIO={min:120,w/IORDY:120}, tDMA={min:120,rec:120}
 PIO modes:  pio0 pio3 pio4
 DMA modes:  mdma0 mdma1 mdma2
 UDMA modes: udma0 udma1 udma2 udma3 udma4 udma5 *udma6
 AdvancedPM=no WriteCache=enabled
 Drive conforms to: Unspecified:  ATA/ATAPI-1,2,3,4,5,6,7
"""

sda_2 = """
/dev/sda:
 Model=ATA VBOX HARDDISK, FwRev=1.0, SerialNo=9876543210
 Config={ HardSect NotMFM HideSecRot }
 RawCHS=16383/16/63, TrkSize=63, SectSize=512
 Transport=ATA, SFF=0x3, SATAPI=0
"""


dict_output_first = {
    '/dev/sda': sda,
    '/dev/sdb': sdb,
    '/dev/sdc': sdc,
    '/dev/sdd': sdd,
}

dict_output_second = {
    '/dev/sda': sda_2,
    '/dev/sdb': sdb_2,
    '/dev/sdc': sdc,
    '/dev/sdd': sdd,
}

print(False == 'refd')