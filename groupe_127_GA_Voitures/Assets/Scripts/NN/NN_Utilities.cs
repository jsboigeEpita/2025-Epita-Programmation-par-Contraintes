using System.IO;
using UnityEngine;

public static class NN_Utilities
{
    private static string saveFilePath = Application.persistentDataPath;

    public static void SaveNN(string fileName, NN nn)
    {
        string json = JsonUtility.ToJson(nn);
        File.WriteAllText(Path.Combine(saveFilePath, fileName), json);
    }

    public static NN LoadNN(string fileName)
    {
        if (!File.Exists(Path.Combine(saveFilePath, fileName)))
        {
            return null;
        }
        string json = File.ReadAllText(Path.Combine(saveFilePath, fileName));
        NN network = JsonUtility.FromJson<NN>(json);
        return network;
    }
}
