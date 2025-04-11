def complex(
    param1, param2, param3, param4, param5, param6, param7, param8, param9, param10
):
    # --- Multi-parameter logic replacements (replacing 10 single-param blocks) ---

    # 2 of 3-parameter testing
    if param1 == "p1_val0" and param2 == "p2_val0" and param3 == "p3_val0":
        print("param1, param2, and param3 are all zero")
    if param4 == "p4_val4" and param5 == "p5_val4" and param6 == "p6_val4":
        print("param4, param5, and param6 are all 4")

    # 2 of 4-parameter testing
    if (
        param1 == "p1_val1"
        and param2 == "p2_val1"
        and param3 == "p3_val1"
        and param4 == "p4_val1"
    ):
        print("First four params are all 1")
    if (
        param7 == "p7_val2"
        and param8 == "p8_val2"
        and param9 == "p9_val2"
        and param10 == "p10_val2"
    ):
        print("Last four params are all 2")

    # 2 of 5-parameter testing
    if (
        param1 == "p1_val3"
        and param2 == "p2_val3"
        and param3 == "p3_val3"
        and param4 == "p4_val3"
        and param5 == "p5_val3"
    ):
        print("First five params are all 3")
    if (
        param6 == "p6_val6"
        and param7 == "p7_val6"
        and param8 == "p8_val6"
        and param9 == "p9_val6"
        and param10 == "p10_val6"
    ):
        print("Last five params are all 6")

    # 1 of 6-parameter testing
    if (
        param1 == "p1_val9"
        and param2 == "p2_val9"
        and param3 == "p3_val9"
        and param4 == "p4_val9"
        and param5 == "p5_val9"
        and param6 == "p6_val9"
    ):
        print("First six params are all max")

    # --- Additional 5 three-parameter tests ---
    if param1 == "p1_val2" and param4 == "p4_val2" and param7 == "p7_val2":
        print("param1, param4, and param7 are all 2")
    if param2 == "p2_val9" and param5 == "p5_val9" and param8 == "p8_val9":
        print("param2, param5, and param8 are all max")
    if param3 == "p3_val0" and param6 == "p6_val0" and param9 == "p9_val0":
        print("param3, param6, and param9 are all zero")
    if param8 == "p8_val1" and param10 == "p10_val1" and param1 == "p1_val1":
        print("param8, param10, and param1 are all 1")
    if param4 == "p4_val4" and param5 == "p5_val4" and param6 == "p6_val4":
        print("param4, param5, and param6 are all 4 again")

    # --- Deep nested logic ---
    if param1 == "p1_val1":
        if param2 == "p2_val2":
            if param3 == "p3_val3":
                if param4 == "p4_val4":
                    print("param1-4 are sequentially increasing")

    # --- Remaining original logic (kept for completeness) ---
    # param7 and param8 logic
    if param7 == "p7_val3" and param8 == "p8_val3":
        print("param7 and param8 are both 3")
    elif param7 == "p7_val5" and param8 == "p8_val5":
        print("param7 and param8 are both 5")
    elif param7 == "p7_val9":
        print("param7 is max")
    else:
        print("param7 is something else")

    if param8 == "p8_val0":
        print("param8 is zero")
    elif param8 == "p8_val9":
        print("param8 is max")
    else:
        print("param8 is mid")

    # param9 and param10 logic
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

    if param10 == "p10_val9":
        print("param10 is max")
    elif param10 == "p10_val1":
        print("param10 is one")
    elif param10 == "p10_val5":
        print("param10 is halfway")
    else:
        print("param10 is something else")
