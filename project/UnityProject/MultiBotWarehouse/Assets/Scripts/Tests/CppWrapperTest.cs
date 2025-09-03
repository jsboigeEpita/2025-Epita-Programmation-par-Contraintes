using System.Runtime.InteropServices;
using UnityEngine;

public class CppWrapperTest : MonoBehaviour
{
    [DllImport("Dll1")]
    private static extern int coucou(int lala);

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        Debug.Log(coucou(0));
        Debug.Log(coucou(5));
        Debug.Log(coucou(21));
        Debug.Log(coucou(11));
    }
}
