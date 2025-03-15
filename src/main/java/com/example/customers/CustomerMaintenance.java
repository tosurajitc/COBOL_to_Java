package com.example.customers;

import java.io.RandomAccessFile;
import java.io.IOException;
import java.util.Scanner;

public class CustomerMaintenance {

    private static final String CUSTOMER_FILE = "custfile.dat";
    private static final int RECORD_LENGTH = 100;

    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(System.in)) {
            System.out.println("Customer Maintenance Application");
            System.out.println("Enter 'X' to exit.");
            
            boolean running = true;
            while (running) {
                System.out.print("Enter Customer ID: ");
                String customerId = scanner.next().toUpperCase();
                
                if (customerId.equals("X")) {
                    running = false;
                    continue;
                }
                
                try {
                    Customer customer = readCustomer(customerId);
                    displayCustomer(customerId, customer);
                } catch (IOException e) {
                    System.out.println("Error reading customer record: " + e.getMessage());
                }
            }
        }
    }

    private static Customer readCustomer(String customerId) throws IOException {
        try (RandomAccessFile file = new RandomAccessFile(CUSTOMER_FILE, "r")) {
            int recordNumber = Integer.parseInt(customerId) - 1;
            long byteOffset = recordNumber * RECORD_LENGTH;
            file.seek(byteOffset);
            byte[] record = new byte[RECORD_LENGTH];
            file.readFully(record);
            return parseCustomerRecord(record);
        }
    }

    private static Customer parseCustomerRecord(byte[] record) {
        Customer customer = new Customer();
        
        // Parse customer ID
        String id = new String(record, 0, 6).trim();
        customer.setId(id);

        // Parse customer name
        String name = new String(record, 6, 20).trim();
        customer.setName(name);

        // Parse address
        String address = new String(record, 26, 20).trim();
        customer.setAddress(address);

        // Parse city
        String city = new String(record, 46, 15).trim();
        customer.setCity(city);

        return customer;
    }

    private static void displayCustomer(String customerId, Customer customer) {
        System.out.println("\nCustomer Information:");
        System.out.println("Customer ID: " + customerId);
        System.out.println("Name: " + customer.getName());
        System.out.println("Address: " + customer.getAddress());
        System.out.println("City: " + customer.getCity());
    }

    private static class Customer {
        private String id;
        private String name;
        private String address;
        private String city;

        // Getters and Setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getAddress() { return address; }
        public void setAddress(String address) { this.address = address; }
        public String getCity() { return city; }
        public void setCity(String city) { this.city = city; }
    }
}
