import msvcrt as m # temp


opcodesToName = {0x00:"ActionEnd", 0x04:"NextFrame", 0x05:"PreviousFrame", 0x06:"Play", 0x07:"Stop", 0x08:"ToggleQuality", 0x09:"StopSounds", 0x0A:"Add", 0x0B:"Subtract", 0x0C:"Multiply", 0x0D:"Divide", 0x0E:"Equals", 0x0F:"Less", 0x10:"And", 0x11:"Or", 0x12:"Not", 0x13:"StrEquals", 0x14:"StrLength", 0x15:"StrExtract", 0x17:"Pop", 0x18:"ToInt", 0x1C:"GetVar", 0x1D:"SetVar", 0x20:"SetTarget2", 0x21:"StrAdd", 0x22:"GetProperty", 0x24:"CloneSprite", 0x25:"RemoveSprite", 0x26:"Trace", 0x27:"StartDrag", 0x28:"EndDrag", 0x29:"StringLess", 0x2A:"Throw", 0x2B:"CastOp", 0x2C:"Implements", 0x30:"RandNum", 0x31:"MbStrLen", 0x32:"CharToAscii", 0x33:"AsciiToChar", 0x34:"GetTime", 0x35:"MBStringExtract", 0x36:"MBCharToAscii", 0x37:"MBAsciiToChar", 0x3A:"Delete", 0x3B:"Delete2", 0x3C:"DefineLocal", 0x3D:"CallFunc", 0x3E:"Return", 0x3F:"Mod", 0x40:"NewObject", 0x41:"DefineLocal2", 0x42:"InitArray", 0x43:"InitObject", 0x44:"TypeOf", 0x45:"TargetPath", 0x46:"Enumerate", 0x47:"Add2", 0x48:"Less2", 0x49:"Equals2", 0x4A:"ToNum", 0x4B:"ToStr", 0x4C:"PushDuplicate", 0x4D:"StackSwap", 0x4E:"GetMember", 0x4F:"SetMember", 0x50:"Increment", 0x51:"Decrement", 0x52:"CallMethod", 0x53:"NewMethod", 0x54:"InstanceOf", 0x55:"Enumerate2", 0x60:"BitwiseAnd", 0x61:"BitwiseOr", 0x62:"BitwiseXor", 0x63:"BitwiseLeftShift", 0x64:"SignedBitwiseRightShift", 0x65:"UnsignedBitwiseRightShift", 0x66:"StrictEquals", 0x67:"TypedGreaterThan", 0x68:"StringGreaterThan", 0x69:"Extends", 0x81:"GoToFrame", 0x83:"GetURL", 0x87:"StoreRegister", 0x88:"ConstantPool", 0x8A:"WaitForFrame", 0x8B:"SetTarget", 0x8C:"GoToLabel", 0x8D:"WaitForFrame2", 0x8E:"DefineFunction2(Block)", 0x94:"With", 0x96:"Push", 0x99:"Branch", 0x9A:"GetURL2", 0x9B:"DefineFunction(Block)", 0x9D:"If", 0x9E:"Call", 0x9F:"GoToFrame2"}

opcodesWithoutExtData = {"ActionEnd":0x00, "Play":0x06, "Stop":0x07, "Add":0x0A, "Subtract":0x0B, "Not":0x12, "Pop":0x17, "GetVar":0x1C, "SetVar":0x1D, "Delete":0x3A, "DefineLocal":0x3C,"CallFunc":0x3D, "Return":0x3E, "NewObject":0x40, "DefineLocal2":0x41, "InitArray":0x42, "Add2":0x47, "Less2":0x48, "Equals2":0x49, "GetMember":0x4E, "SetMember":0x4F, "Increment":0x50, "CallMethod":0x52, "NewMethod":0x53, "TypedGreaterThan":0x67} # List severely incomplete. Things will definitely not decompile correctly in its current state

opcodesWithOneItem = {"GoToFrame":"Constant", "StoreRegister":"Register", "GoToFrame2":"Constant", "GoToLabel":"Str", "If":"unk_2", "Branch":"sint"} # these bastards I guess only have the frame number

opcodesWithAssumedDatatypes = {"DefineFunction(Block)":["Str", "param", "length"], "DefineFunction2(Block)":["Str", "unk_2", "length"]}

nameToOpcodes = {v: k for k, v in opcodesToName.items()}

datatypes = {0x00:"Str", 0x01:"Float", 0x02:"Null", 0x03:"Undefined", 0x04:"Register", 0x05:"Boolean", 0x06:"Double", 0x07:"Int", 0x08:"Constant", 0x09:"Large Constant", "unk_1":"unk_1", "unk_2":"unk_2", "param":"param", "length":"length"} # Note: datatypes that don't start with a hex value are just for usage in defining unflagged values

datatypeLengths = {"Str":2, "Float":4, "Null":0, "Undefined":0, "Register":1, "Boolean":1, "Double":8, "Int":4, "Constant":1, "Large Constant":2, "unk_1":1, "unk_2":2, "length":2, "param":2, "sint":2}

def test():
    print("This is the first dictionary")
    for k, v in opcodesToName.items():
        print("0x",format(k, "0>2X"), " ", v, sep='')
    print("\nThis is the second dictionary")
    for k, v in nameToOpcodes.items():
        print(k ," 0x",format(v, "0>2X"), sep='')

def parseFunc(numActions, data, symbols, endianess):
    if endianess == "big":
        dumb_endianess = "little"
    else:
        dumb_endianess = "big"
    for x in range(numActions):
        counter = 4
        actionLength = int.from_bytes(data[:4], byteorder=endianess)
        print("\nAction 0x", format(x, "0>2X"), ":", "# Length: ", actionLength, sep='')
        print("----------------------------------------------------------")
        disassembly = []
        while counter <= actionLength + 3:
            try:
                opcode = check_opcode(data[counter])
            except:
                print(data[counter])
                opcode = ("Unknown Opcode: 0x" + format(int.from_bytes(data[counter], byteorder=endianess), "0>4X"))
            print("\n\nOpcode:", opcode, end='')
            counter += 1

            if opcode not in opcodesWithoutExtData:
                if opcode in opcodesWithOneItem:
                    length = check_length(data[counter:counter + 2], dumb_endianess)
                    print(", Length: ", length, end='', sep='')
                    datatype = opcodesWithOneItem[opcode]
                    datatypeLength = datatypeLengths[datatype]
                    print(", Datatype: ", datatype, end='', sep='')
                    counter += 2
                    value = data[counter:counter + length]
                    print(", Value: ", value, end='', sep='')
                    counter += datatypeLength

                elif opcode in opcodesWithAssumedDatatypes:
                    if opcode == "DefineFunction(Block)":
                        length = check_length(data[counter:counter + 2], dumb_endianess)
                        counter += 2
                        symbol = int.from_bytes(data[counter:counter + datatypeLengths["Str"]], byteorder=dumb_endianess)
                        counter += datatypeLengths["Str"]
                        params = int.from_bytes(data[counter:counter + datatypeLengths["param"]], byteorder=dumb_endianess)
                        counter += datatypeLengths["param"]
                        funcLength = int.from_bytes(data[counter:counter + datatypeLengths["length"]], byteorder=dumb_endianess)
                        counter += datatypeLengths["length"]
                        paramList = []
                        for x in range(params):
                            paramList.append("Param " + str(x) + ": " + str(data[counter:counter + datatypeLengths["Str"]]) + "\n")
                            counter += datatypeLengths["Str"]
                            # m.getch()
                        print(", NumParams: ", format(params, "0>2X"), ",Param Names: (", paramList, "), Function Length: ", funcLength, sep='')

                    elif opcode == "DefineFunction2(Block)":
                        length = check_length(data[counter:counter + 2], dumb_endianess)
                        counter += 2
                        symbol = int.from_bytes(data[counter:counter + datatypeLengths["Str"]], byteorder=dumb_endianess)
                        counter += datatypeLengths["Str"]

                        params = int.from_bytes(data[counter:counter + 2], byteorder=dumb_endianess)
                        counter += 2

                        unk_1 = int.from_bytes(data[counter:counter + 1], byteorder=dumb_endianess)
                        counter += 1

                        flags = int.from_bytes(data[counter:counter + datatypeLengths["Large Constant"]], byteorder=dumb_endianess)
                        counter += datatypeLengths["Large Constant"]

                        print(", Symbol: 0x", format(symbol, "0>4X"), ", NumParams: 0x", format(params, "0>4X"), ", Unk_1: 0x", format(unk_1, "0>2X"), ", Flags: 0x", format(flags, "0>4X"), sep='', end='')

                        if params > 0:
                            print(", Params: (", end='')
                            for x in range(params):
                                register = int.from_bytes(data[counter:counter + 1], byteorder=dumb_endianess)
                                counter += 1
                                reg_sym = int.from_bytes(data[counter:counter + 2], byteorder=dumb_endianess)
                                counter += 2
                                print("r", register, ":", format(reg_sym, "0>4X"), sep='', end='')
                                if x != params - 1:
                                    print(', ', end='')
                                else:
                                    print(')', end='')

                        func_len = int.from_bytes(data[counter:counter + 2], byteorder=dumb_endianess)
                        counter += 2

                        print(", func_len: 0x", format(func_len, "0>4X"), sep='', end='')
                        
                    else:
                        datatypes = opcodesWithAssumedDatatypes[opcode]
                        length = check_length(data[counter:counter + 2], dumb_endianess)
                        counter += 2
                        stuff = []
                        for x in datatypes:
                            stuff.append(int.from_bytes(data[counter:counter + datatypeLengths[x]], byteorder=dumb_endianess))
                            counter += datatypeLengths[x]
                        print("AAAHHHHHH", stuff)

                else:
                    length = check_length(data[counter:counter + 2], dumb_endianess)
                    print(", Length: ", length, end='', sep='')
                    counter += 2
                    while length != 0:
                        datatype, datatypeLength = check_datatype(data[counter])
                        print(", Datatype: ", datatype, end='', sep='')
                        counter += 1
                        length -= 1
                        value = int.from_bytes(data[counter:counter + datatypeLength], byteorder=dumb_endianess)
                        if datatype == "Str":
                            try:
                                value = symbols[value]
                            except:
                                pass
                        print(", Value: ", format(value, "0>4X"), end='', sep='')
                        counter += datatypeLength
                        length -= datatypeLength

        if counter % 4 != 0:
            counter += (4 - counter % 4)
        data = data[counter:]

def check_opcode(data):
    global opcodesToName
    return opcodesToName[data]

def check_length(data, endianess):
    return int.from_bytes(data, byteorder=endianess)

def check_datatype(data):
    global datatypes
    global datatypeLengths
    return datatypes[data], datatypeLengths[datatypes[data]]

something_dumb = bytes.fromhex('0000000307000000000000249603000060001C960300000C004E96080007010000000061001C96030000620052170000000000249603000060001C960300001C004E96080007010000000061001C96030000620052170000000000088C02002C00060000000000078C020014000000000000000306000000000000088C02003400060000000000249603000060001C960300001C004E96080007010000000061001C960300006300521700000000001D960300001C001C96080007010000000061001C9603000062005217000000000000000029960D00070200000007010000000060001C9603000030004E9603000035004E9603000064005217000000000000000019960B0000140007010000000060001C96030000650052170000000000000009EA9B0600B8000000070096020008663E009B0A00B9000200BA00BB000100008E0900BC000000022A003E0096050007000000008701000117960400040108671C48129D0200220096020008681C960700040107000000004F9602000401508701000117990200D0FF008E0C00BD000100022A0001BE00500096020008681C96020004014E960700070100000008691C960200086A52129D02001B00960200086B1C9604000401086B1C96020004014E504F9902001200960200086B1C960700040107000000004F008E0C00BF000100022A0001BE001700960200086B1C96020004014E9605000701000000493E008E0C00C0000100022A0001BE001700960200086B1C96020004014E9605000700000000673E008E0900B4000000036A012F009606000402086C05004F9606000402086D05004F9606000402086E05004F960B00085B0701000000040108645217008E0C00B6000100032A0102C10015009606000401086F05014F9606000401087004024F009B0600C200000021009609000871070100000008721C96020008734E96020008744E96020008755217009B0600C300000021009609000876070100000008721C96020008734E96020008744E96020008755217009B0600C400000021009609000877070100000008721C96020008734E96020008744E96020008755217009B0600C500000021009609000878070100000008721C96020008734E96020008744E96020008755217009B0600C600000021009609000879070100000008721C96020008734E96020008744E96020008755217009B0600C70000002100960900087A070100000008721C96020008734E96020008744E96020008755217008E0C00C8000100022A0001C9002300960B000401087B070200000008721C96020008734E96020008744E96020008755217008E0C00CA000100022A0001C9002300960B000401087C070200000008721C96020008734E96020008744E96020008755217008E0C00CB000100022A0001C9002300960B000401087D070200000008721C96020008734E96020008744E96020008755217008E0C00CC000100022A0001C9002300960B000401087E070200000008721C96020008734E96020008744E96020008755217008E0F00CD00020004290103C90000820055009606000402087F05014F9606000402088004034F960400040108818E0900000000000329012C009604000402086F4E129D02001E00960400040208704E960700070100000008823D17960400040108813A17004F008E1800CE000500072A0001CF0005D00003D10004D20006D300BC00960200040187010002179607000401070000000067129D02003B00960400040104056712129D02000F009602000403870100021799020018009604000401040467129D02000A00960200040687010002179902005F009607000401070000000048129D02004E009609000401070000000004050B4812129D02001500960700070000000004030B870100021799020024009609000401070000000004040B48129D02001000960700070000000004060B870100021796020004023E008E0F00D4000200032A0002D50001D60030009607000401070A0000004812129D02000E0096040004020401473E990200100096040004020883479602000401473E008E0F00D7000200032A0002D50001D6005600960700040107640000004812129D02000E0096040004020401473E99020036009607000401070A0000004812129D0200140096040004020883479602000401473E990200100096040004020884479602000401473E008E0C0062000100022A0001D8005700960400040108854E963D000886070000000007FF00000007FF00000007FF000000070100000006273108AC1C5AECBF06273108AC1C5AECBF06273108AC1C5AECBF070800000008721C96020008874E9602000888534F008E0C0063000100022A0001D8005700960400040108854E963D0008860700000000071D000000071D000000071D000000070100000006273108AC1C5AEC3F06273108AC1C5AEC3F06273108AC1C5AEC3F070800000008721C96020008874E9602000888534F008E0C00D9000100022A0001D8005700960400040108854E963D0008860700000000071D000000071D000000071D000000070100000006273108AC1C5AEC3F06273108AC1C5AEC3F06273108AC1C5AEC3F070800000008721C96020008874E9602000888534F008E0C00DA000100022A0001D8005700960400040108854E963D000886070000000007FF00000007FF00000007FF000000070100000006273108AC1C5AECBF06273108AC1C5AECBF06273108AC1C5AECBF070800000008721C96020008874E9602000888534F0096020008891C960400088A05004F960700088B07000000003C960700088C07010000003C960700088D07020000003C960700088E07030000003C960700088F07040000003C960700089007050000003C960700089107060000003C960700089207070000003C960700089307080000003C960700089407090000003C9607000895070A0000003C9607000896070B0000003C9607000897070C0000003C960700089807530000003C9607000899075A0000003C960700089A07570000003C960700089B07410000003C960700089C07510000003C960700089D07450000003C960700089E07250000003C960700089F07270000003C96070008A007260000003C96070008A107280000003C960400086808A11C96020008A01C960200089F1C960200089E1C960200089D1C960200089C1C960200089B1C960200089A1C96020008991C96020008981C960500070A000000423C960400086B08971C960700070100000008A2403C96020008891C960400086C05004F96020008891C96040008A305004F96020008891C960400086E05004F96020008891C960400087F05004F96020008891C960700088007000000004F96020008891C960400086F05004F96020008891C960700087007000000004F96020008891C96070008A407000000004F96020008891C96070008A507000000004F96020008891C96070008A607000000004F96020008891C96070008A707000000004F96020008891C96070008A807000000004F96020008891C96070008A907000000004F96020008891C96070008AA07000000004F96020008891C96070008AB07000000004F96020008891C96070008AC07000000004F96020008891C96070008AD07000000004F96020008891C96070008AE07000000004F96020008891C96070008AF07000000004F96020008891C96040008B005004F96020008891C96040008B105004F96020008891C96040008B205004F96020008891C96040008B305004F96020008B41C960A000208B4070300000008721C96020008734E96020008744E96020008B5521796020008B61C960A000208B6070300000008721C96020008734E96020008744E96020008B5521796020008891C96070008B707080000004F000000000000008D96070008DB07000000003C96020008DB1C96020008891C96020008B74E48129D02003F0096040008DC08611C96040008DD08DB1C960500070100000047474E3C9609000803070100000008DC1C9602000864521796040008DB08DB1C501D990200A8FF96090008030701000000084A1C960200086452179609000803070100000008491C960200086452170000000000000000170796080007000000000061001C96030000C50052170000000000008D96070008DB07000000003C96020008DB1C96020008891C96020008B74E48129D02003F0096040008DC08611C96040008DD08DB1C960500070100000047474E3C9609000804070100000008DC1C9602000864521796040008DB08DB1C501D990200A8FF96090008040701000000084A1C960200086452179609000804070100000008491C960200086452170000000000000000170796080007000000000061001C96030000C7005217000000')
parseFunc(15, something_dumb, "a", "big")