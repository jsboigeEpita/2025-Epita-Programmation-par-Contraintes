using UnityEngine;

public class Wharehouse
{
    public static int gridScale = 5;

    public static Vector3Int convertGridPosition(Vector3 position)
    {
        return new Vector3Int(Mathf.FloorToInt(position.x / gridScale), Mathf.FloorToInt(position.y / gridScale), Mathf.FloorToInt(position.z / gridScale));
    }
}
