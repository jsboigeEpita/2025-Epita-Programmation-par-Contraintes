def calculate_discount(
    price: float, customer_type: str, is_member: bool = False, y: float = 0.0
):
    if customer_type == "student":
        discount = 0.2
    elif customer_type == "senior":
        discount = 0.3
    else:
        discount = 0.1

    if is_member:
        discount += 0.05

    # 2-wise interaction: customer_type and y
    if customer_type == "student" and y == 3:
        print("Student special y=3")

    # 2-wise interaction: is_member and y
    if is_member and y == 5:
        print("Member bonus for y=5")

    # 2-wise interaction: price and customer_type
    if price > 100 and customer_type == "senior":
        print("Senior high spender")

    # 3-wise interaction: price, customer_type, is_member
    if price > 200 and customer_type == "student" and is_member:
        print("Super student member discount")

    # 3-wise interaction: price, y, is_member
    if price < 50 and y == 1 and not is_member:
        print("Low price, y=1, not a member")

    # Original y-based logic
    if y == 3:
        print("coucou")
    elif y == 5:
        print("HI")
    else:
        print("lule")

    return price * (1 - discount)


def configure_volume(Type, Size, Format_method, File_system, Cluster_size, Compression):
    if Type == "RAID-5":
        print("RAID-5 requires at least 3 disks.")
    elif Type == "Mirror":
        print("Mirroring enabled.")
    elif Type == "Striped" and Compression == "On":
        print("Striped volumes can't be compressed.")

    if Size >= 10000:
        print("Large volume detected.")
    elif Size == 10:
        print("Tiny volume warning.")

    if Format_method == "Quick":
        print("Quick format selected.")
    else:
        print("Slow format may take longer.")

    if File_system == "FAT":
        print("FAT is outdated.")
    elif File_system == "NTFS" and Compression == "On":
        print("NTFS supports compression.")

    if Cluster_size == 512:
        print("Smallest cluster size.")
    elif Cluster_size > 8192:
        print("Large cluster size may waste space.")

    if Compression == "On":
        print("Compression enabled.")
    else:
        print("No compression.")

    return "Configuration complete"
