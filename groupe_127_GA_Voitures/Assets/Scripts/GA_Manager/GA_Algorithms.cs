using System.Collections.Generic;

public static class GA_Algorithms
{
    public static List<NN> basic_mutation(List<NN> dads, float mutation_proba, float mutation_amount)
    {
        List<NN> result = new List<NN>();
        for (int i = 0; i < dads.Count; i++)
        {
            for (int j = (dads.Count - i) / 3; j >= 0; j--)
            {
                NN child = dads[i % dads.Count].DeepCopy();
                child.Mutate(mutation_proba, mutation_amount);
                result.Add(child);
            }
        }
        return result;
    }

    public static List<NN> two_parents_mutation_top_n_dads(List<NN> dads, int n_dads, float mutation_proba, float mutation_amount)
    {
        List<NN> result = new List<NN>();
        for (int i = 0; i < n_dads; i++)
        {
            for (int j = i + 1; j < n_dads; j++)
            {
                NN averaged_child = average_two_nn(dads[i], dads[j]);
                averaged_child.Mutate(mutation_proba, mutation_amount);
                result.Add(averaged_child);
            }
        }
        return result;
    }

    private static NN average_two_nn(NN nn1, NN nn2)
    {
        NN result = nn1.DeepCopy();
        for (int i = 0; i < nn1.layers.Count; i++)
        {
            Layer result_layer = result.layers[i];
            for (int j = 0; j < result_layer.neurons.Length; j++)
            {
                Neuron result_neuron = result_layer.neurons[j];
                for (int k = 0; k < result_neuron.weights.Length; k++)
                {
                    result_neuron.weights[i] = (result_neuron.weights[i] + nn2.layers[i].neurons[j].weights[k]) / 2f;
                }
            }
        }
        return result;
    }
}
