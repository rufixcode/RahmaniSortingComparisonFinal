public class RahmaniSort {
    public static void sort(int[] a) {
        int n = a.length;
        for (int i = 2; i < n; i++) {
            if (a[i] >= a[i - 1]) {
                continue; // Skip if already in order
            }
            int key = a[i];
            int j;
            if (a[i] <= a[1]) {
                j = 1;
            } else {
                j = iSearch(a, 1, i - 1, key);
            }
            int k = i;
            while (k > j) {
                a[k] = a[k - 1];
                k--;
            }
            a[j] = key;
        }
    }

    // Binary search-based insertion index finder
    private static int iSearch(int[] a, int lower, int upper, int key) {
        while (lower <= upper) {
            int mid = (lower + upper) / 2;
            if (a[mid] == key) {
                return mid + 1;
            } else if (a[mid] < key) {
                lower = mid + 1;
            } else {
                upper = mid - 1;
            }
        }
        return lower;
    }
}