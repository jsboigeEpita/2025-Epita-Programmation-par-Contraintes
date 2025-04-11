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
