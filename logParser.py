from logStorage import logStorage

import gem5.util.protolib as protolib
import sys
import gem5.util.inst_dep_record_pb2 as inst_dep_record_pb2
import os
import subprocess
import gem5.util.packet_pb2 as packet_pb2

class logParser:
    def __init__(self, logStorage, args):
        self.logStorage = logStorage
        self.args = args
        self.uuid = args.uuid[0]
        
    def run(self, results):
        for index in results:
            self.__runSingle(index)
            
    def __runSingle(self, index):
        path = 'data/' + self.uuid + '/logs/' + str(index) + '/'
        protoPath = path + 'm5out/'
        depInput = protoPath + 'system.cpu.traceListener.deptrace.proto.gz'
        instInput = protoPath + 'system.cpu.traceListener.fetchtrace.proto.gz'
        depOutput = path + 'deptrace'
        instOutput = path + 'insttrace'
        self.__dep_trace(depInput, depOutput)
        self.__inst_trace(instInput, instOutput)
    
    def __dep_trace(self, input, output):
        # Open the file on read mode
        proto_in = protolib.openFileRd(input)

        try:
            ascii_out = open(output, 'w')
        except IOError:
            print("Failed to open ", output, " for writing")
            exit(-1)

        # Read the magic number in 4-byte Little Endian
        magic_number = proto_in.read(4).decode()

        if magic_number != "gem5":
            print("Unrecognized file")
            exit(-1)

        print("Parsing packet header")

        # Add the packet header
        header = inst_dep_record_pb2.InstDepRecordHeader()
        protolib.decodeMessage(proto_in, header)

        print("Object id:", header.obj_id)
        print("Tick frequency:", header.tick_freq)

        print("Parsing packets")

        print("Creating enum value,name lookup from proto")
        enumNames = {}
        desc = inst_dep_record_pb2.InstDepRecord.DESCRIPTOR
        for namestr, valdesc in list(desc.enum_values_by_name.items()):
            print('\t', valdesc.number, namestr)
            enumNames[valdesc.number] = namestr

        num_packets = 0
        num_regdeps = 0
        num_robdeps = 0
        packet = inst_dep_record_pb2.InstDepRecord()

        # Decode the packet messages until we hit the end of the file
        while protolib.decodeMessage(proto_in, packet):
            num_packets += 1

            # Write to file the seq num
            ascii_out.write('%s' % (packet.seq_num))
            # Write to file the pc of the instruction, default is 0
            if packet.HasField('pc'):
                ascii_out.write(',%s' % (packet.pc))
            else:
                ascii_out.write(',0')
            # Write to file the weight, default is 1
            if packet.HasField('weight'):
                ascii_out.write(',%s' % (packet.weight))
            else:
                ascii_out.write(',1')
            # Write to file the type of the record
            try:
                ascii_out.write(',%s' % enumNames[packet.type])
            except KeyError:
                print("Seq. num", packet.seq_num, "has unsupported type", \
                    packet.type)
                exit(-1)


            # Write to file if it has the optional fields physical addr, size,
            # flags
            if packet.HasField('p_addr'):
                ascii_out.write(',%s' % (packet.p_addr))
            if packet.HasField('size'):
                ascii_out.write(',%s' % (packet.size))
            if packet.HasField('flags'):
                ascii_out.write(',%s' % (packet.flags))

            # Write to file the comp delay
            ascii_out.write(',%s' % (packet.comp_delay))

            # Write to file the repeated field order dependency
            ascii_out.write(':')
            if packet.rob_dep:
                num_robdeps += 1
                for dep in packet.rob_dep:
                    ascii_out.write(',%s' % dep)
            # Write to file the repeated field register dependency
            ascii_out.write(':')
            if packet.reg_dep:
                num_regdeps += 1 # No. of packets with atleast 1 register dependency
                for dep in packet.reg_dep:
                    ascii_out.write(',%s' % dep)
            # New line
            ascii_out.write('\n')

        print("Parsed packets:", num_packets)
        print("Packets with at least 1 reg dep:", num_regdeps)
        print("Packets with at least 1 rob dep:", num_robdeps)

        # We're done
        ascii_out.close()
        proto_in.close()
        
    def __inst_trace(self, input, output):
        # Open the file in read mode
        proto_in = protolib.openFileRd(input)

        try:
            ascii_out = open(output, 'w')
        except IOError:
            print("Failed to open ", output, " for writing")
            exit(-1)

        # Read the magic number in 4-byte Little Endian
        magic_number = proto_in.read(4).decode()

        if magic_number != "gem5":
            print("Unrecognized file", input)
            exit(-1)

        print("Parsing packet header")

        # Add the packet header
        header = packet_pb2.PacketHeader()
        protolib.decodeMessage(proto_in, header)

        print("Object id:", header.obj_id)
        print("Tick frequency:", header.tick_freq)

        for id_string in header.id_strings:
            print('Master id %d: %s' % (id_string.key, id_string.value))

        print("Parsing packets")

        num_packets = 0
        packet = packet_pb2.Packet()

        # Decode the packet messages until we hit the end of the file
        while protolib.decodeMessage(proto_in, packet):
            num_packets += 1
            # ReadReq is 1 and WriteReq is 4 in src/mem/packet.hh Command enum
            cmd = 'r' if packet.cmd == 1 else ('w' if packet.cmd == 4 else 'u')
            if packet.HasField('pkt_id'):
                ascii_out.write('%s,' % (packet.pkt_id))
            if packet.HasField('flags'):
                ascii_out.write('%s,%s,%s,%s,%s' % (cmd, packet.addr, packet.size,
                                packet.flags, packet.tick))
            else:
                ascii_out.write('%s,%s,%s,%s' % (cmd, packet.addr, packet.size,
                                            packet.tick))
            if packet.HasField('pc'):
                ascii_out.write(',%s\n' % (packet.pc))
            else:
                ascii_out.write('\n')

        print("Parsed packets:", num_packets)

        # We're done
        ascii_out.close()
        proto_in.close()