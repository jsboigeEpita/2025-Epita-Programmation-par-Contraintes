using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName = "Furnitures", menuName = "Scriptable Objects/Furnitures")]
public class Furnitures : ScriptableObject
{
    public List<GameObject> furnitures;
    public List<string> names;
}
