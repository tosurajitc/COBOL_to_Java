package com.company.customer;

import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

class Customer {
    private String name;
    private String address;
    private String city;

    public Customer(String name, String address, String city) {
        this.name = name;
        this.address = address;
        this.city = city;
    }

    public String getName() {
        return name;
    }

    public String getAddress() {
        return address;
    }

    public String getCity() {
        return city;
    }
}

public class CustomerMaintenance {
    private Map<String, Customer> customerRecords;
    private Scanner scanner;

    public CustomerMaintenance() {
        this.scanner = new Scanner(System.in);
        this.customerRecords = new HashMap<>();
        initializeSampleData();
    }

    private void initializeSampleData() {
        // Sample customer data for demonstration
        customerRecords.put("1", new Customer("John Doe", "123 Main St", "New York"));
        customerRecords.put("2", new Customer("Jane Smith", "456 Oak Ave", "Chicago"));
        // Add more customers as needed
    }

    public void run() {
        System.out.println("Customer Maintenance System");
        System.out.println("---------------------------");

        while (true) {
            System.out.print("Enter Customer ID (or 'X' to exit): ");
            String customerId = scanner.next().toUpperCase();

            if (customerId.equals("X")) {
                System.out.println("Exiting program.");
                break;
            }

            if (customerRecords.containsKey(customerId)) {
                Customer customer = customerRecords.get(customerId);
                System.out.println("\nCustomer Information:");
                System.out.println("---------------------");
                System.out.println("Name: " + customer.getName());
                System.out.println("Address: " + customer.getAddress());
                System.out.println("City: " + customer.getCity());
                System.out.println("---------------------\n");
            } else {
                System.out.println("CUSTOMER NOT FOUND\n");
            }
        }

        scanner.close();
    }

    public static void main(String[] args) {
        CustomerMaintenance maintenance = new CustomerMaintenance();
        maintenance.run();
    }
}