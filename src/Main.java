// SortFromFile.java
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        String filename = "input.txt"; // Ensure the file exists in the project directory
        List<int[]> datasets = readDataFromFile(filename);

        for (int[] data : datasets) {
            System.out.println("Sorting " + data.length + " elements...");

            // Copy arrays for fair comparison
            int[] arrayRahmani = Arrays.copyOf(data, data.length);
            int[] arraySequential = Arrays.copyOf(data, data.length);
            int[] arrayBinary = Arrays.copyOf(data, data.length);
            int[] arrayMerge = Arrays.copyOf(data, data.length);
            int[] arrayQuick = Arrays.copyOf(data, data.length);

            // Measure execution times
            measureSortTime("Rahmani Sort", () -> RahmaniSort.sort(arrayRahmani));
            measureSortTime("Sequential Insertion Sort", () -> InsertionSortSequential.sort(arraySequential));
            measureSortTime("Binary Insertion Sort", () -> InsertionSortBinary.sort(arrayBinary));
            measureSortTime("Merge Sort", () -> MergeSort.sort(arrayMerge, 0, arrayMerge.length - 1));
            measureSortTime("Quick Sort", () -> QuickSort.sort(arrayQuick, 0, arrayQuick.length - 1));

            System.out.println();
        }
    }

    private static List<int[]> readDataFromFile(String filename) throws IOException {
        List<int[]> datasets = new ArrayList<>();
        BufferedReader reader = new BufferedReader(new FileReader(filename));
        String line;
        while ((line = reader.readLine()) != null) {
            String[] parts = line.split(" ");
            int[] data = Arrays.stream(parts).mapToInt(Integer::parseInt).toArray();
            datasets.add(data);
        }
        reader.close();
        return datasets;
    }

    private static void measureSortTime(String name, Runnable sortMethod) {
        long startTime = System.nanoTime();
        sortMethod.run();
        long endTime = System.nanoTime();
        System.out.println(name + " Time: " + (endTime - startTime) / 1e6 + " ms");
    }
}
