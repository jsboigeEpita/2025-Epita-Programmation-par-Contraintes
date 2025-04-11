def complex(
    param1, param2, param3, param4, param5, param6, param7, param8, param9, param10
):
    # --- param1 logic ---
    if param1 == "p1_val0":
        print("param1 is zero")
    elif param1 == "p1_val5":
        print("param1 is halfway")
    elif param1 == "p1_val9":
        print("param1 is max")
    else:
        print(f"param1 is {param1}")

    # --- param2 logic ---
    if param2 in ["p2_val0", "p2_val2", "p2_val4", "p2_val6", "p2_val8"]:
        print("param2 is even")
    else:
        print("param2 is odd")

    # --- param3 logic ---
    if param3 == "p3_val3":
        print("param3 is a magic number")
    elif param3 == "p3_val7":
        print("param3 is a lucky number")
    else:
        print("param3 is normal")

    # --- param4 logic ---
    if param4.startswith("p4_val"):
        idx = int(param4.split("p4_val")[1])
        if idx < 3:
            print("param4 is low")
        elif idx < 7:
            print("param4 is medium")
        else:
            print("param4 is high")

    # --- param5 logic ---
    if param5 == "p5_val0":
        print("param5 is default")
    elif param5 == "p5_val9":
        print("param5 is extreme")
    else:
        print("param5 is custom")

    # --- param6 logic ---
    if param6 == "p6_val1":
        print("param6 is one")
    elif param6 == "p6_val2":
        print("param6 is two")
    elif param6 == "p6_val3":
        print("param6 is three")
    elif param6 == "p6_val4":
        print("param6 is four")
    elif param6 == "p6_val5":
        print("param6 is five")
    elif param6 == "p6_val6":
        print("param6 is six")
    elif param6 == "p6_val7":
        print("param6 is seven")
    elif param6 == "p6_val8":
        print("param6 is eight")
    elif param6 == "p6_val9":
        print("param6 is nine")
    else:
        print("param6 is zero")

    # --- param7 logic ---
    if param7 == "p7_val3" and param8 == "p8_val3":
        print("param7 and param8 are both 3")
    elif param7 == "p7_val5" and param8 == "p8_val5":
        print("param7 and param8 are both 5")
    elif param7 == "p7_val9":
        print("param7 is max")
    else:
        print("param7 is something else")

    # --- param8 logic ---
    if param8 == "p8_val0":
        print("param8 is zero")
    elif param8 == "p8_val9":
        print("param8 is max")
    else:
        print("param8 is mid")

    # --- param9 logic ---
    if param9 == "p9_val7":
        if param10 == "p10_val7":
            print("param9 and param10 are both 7")
        elif param10 == "p10_val0":
            print("param9 is 7 and param10 is 0")
        else:
            print("param9 is 7 and param10 is something else")
    elif param9 == "p9_val0":
        print("param9 is zero")
    else:
        print("param9 is something else")

    # --- param10 logic ---
    if param10 == "p10_val9":
        print("param10 is max")
    elif param10 == "p10_val1":
        print("param10 is one")
    elif param10 == "p10_val5":
        print("param10 is halfway")
    else:
        print("param10 is something else")

    # --- Multi-parameter logic ---
    if param1 == "p1_val2" and param4 == "p4_val2" and param7 == "p7_val2":
        print("param1, param4, and param7 are all 2")

    if param2 == "p2_val9" and param5 == "p5_val9":
        print("param2 and param5 are both max")

    if param3 == "p3_val0" and param6 == "p6_val0" and param9 == "p9_val0":
        print("param3, param6, and param9 are all zero")

    if param8 == "p8_val1" and param10 == "p10_val1":
        print("param8 and param10 are both 1")

    if (
        param1 == "p1_val4"
        and param2 == "p2_val4"
        and param3 == "p3_val4"
        and param4 == "p4_val4"
    ):
        print("First four params are all 4")

    # --- Deep nested logic ---
    if param1 == "p1_val1":
        if param2 == "p2_val2":
            if param3 == "p3_val3":
                if param4 == "p4_val4":
                    print("param1-4 are sequentially increasing")
