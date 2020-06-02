using System;
					
public class Program
{
	public static void Main(string[] args)
        {
            Random rnd = new Random();

            int[] my_arr = new int[30]; 
            int[] my_arr_rev = new int[30];
            int[] my_arr_combined = new int[30];

            for (int i = 0; i < 30; i++) {
              my_arr[i] = rnd.Next(100, 1000);
              int num = my_arr[i];
              int reverse = 0;
              while(Convert.ToBoolean(num)) {
                reverse = reverse * 10 + num % 10;
                num = num / 10; 
              }
              my_arr_rev[i] = reverse;
              my_arr_combined[i] = my_arr_rev[i] + my_arr[i];
            }
            
            int num_even = 0;
            Array.ForEach(my_arr, delegate(int i) { if ((i % 10)%2==0) num_even += 1; });
            Console.WriteLine(num_even);
            
            int sum_ones = 0;
            Array.ForEach(my_arr, delegate(int i) { sum_ones += i%10; });
            Console.WriteLine(num_even);
        }
}
