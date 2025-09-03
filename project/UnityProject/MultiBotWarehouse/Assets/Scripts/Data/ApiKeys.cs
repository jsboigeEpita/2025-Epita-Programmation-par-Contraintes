using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName = "ApiKeys", menuName = "Scriptable Objects/ApiKeys")]
public class ApiKeys : ScriptableObject
{
    public string key;
    public string endpoint;
}
