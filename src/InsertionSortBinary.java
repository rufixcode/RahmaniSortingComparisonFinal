// InsertionSortBinary.java

public class InsertionSortBinary {
    public static void sort(int[] arr) {
        int n = arr.length;
        for (int i = 1; i < n; i++) {
            int key = arr[i];
            int j = binarySearch(arr, 0, i - 1, key); // Find position using binary search
            int k = i;

            // Shift elements to the right
            while (k > j) {
                arr[k] = arr[k - 1];
                k--;
            }
            arr[j] = key;
        }
    }

    private static int binarySearch(int[] arr, int low, int high, int key) {
        while (low <= high) {
            int mid = (low + high) / 2;
            if (arr[mid] == key) return mid + 1;
            if (arr[mid] < key) low = mid + 1;
            else high = mid - 1;
        }
        return low;
    }
}
