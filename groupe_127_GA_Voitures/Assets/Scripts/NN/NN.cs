using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class NN
{
    [SerializeField] public List<Layer> layers;
    public NN()
    {
        this.layers = new List<Layer>();
    }

    public void AddLayer(int n_inputs, int n_outputs, ActivationMethod activationMethod)
    {
        this.layers.Add(new Layer(n_inputs, n_outputs, activationMethod));
    }

    public float[] Forward(float[] inputs)
    {
        // Compute first layer outside loop cause it's the user input
        this.layers[0].Forward(inputs);
        for (int i = 1; i < this.layers.Count; i++)
        {
            this.layers[i].Forward(this.layers[i - 1].outputs);
        }
        return this.layers[this.layers.Count - 1].outputs;
    }

    // MUTATION
    public void Mutate(float proba, float amount)
    {
        foreach (Layer layer in this.layers)
        {
            layer.Mutate(proba, amount);
        }
    }

    // DEEP COPY
    public NN DeepCopy()
    {
        NN result = new NN();
        foreach(Layer layer in this.layers)
        {
            result.layers.Add(layer.DeepCopy());
        }
        return result;
    }
}
