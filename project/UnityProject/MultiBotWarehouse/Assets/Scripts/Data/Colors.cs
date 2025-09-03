using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName = "Colors", menuName = "Scriptable Objects/Colors")]
public class Colors : ScriptableObject
{
    public List<Material> colors;
}
