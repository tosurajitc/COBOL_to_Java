package com.cobol2java.customer;

import java.io.RandomAccessFile;
import java.io.IOException;
import java.util.Scanner;

public class CustomerMaintenance {
    private static final int RECORD_SIZE = 100;
    private RandomAccessFile customerFile;
    private Scanner scanner;
    private Customer currentCustomer;

    public CustomerMaintenance() {
        this.scanner = new Scanner(System.in);
        initializeFile();
    }

    private void initializeFile() {
        try {
            customerFile = new RandomAccessFile("custfile.dat", "rws");
        } catch (IOException e) {
            System.err.println("Error opening file: " + e.getMessage());
            System.exit(1);
        }
    }

    public void processUserInput() {
        while (true) {
            System.out.print("Enter customer ID (or 'X' to exit): ");
            String input = scanner.nextLine().trim().toUpperCase();

            if (input.equals("X")) {
                break;
            }

            try {
                currentCustomer = readCustomer(input);
                if (currentCustomer != null) {
                    displayCustomer(currentCustomer);
                } else {
                    System.out.println("Customer not found.");
                }
            } catch (IOException e) {
                System.err.println("Error reading file: " + e.getMessage());
                System.exit(1);
            }
        }
    }

    private Customer readCustomer(String id) throws IOException {
        int recordNumber = Integer.parseInt(id) - 1;
        long position = recordNumber * RECORD_SIZE;
        customerFile.seek(position);

        byte[] data = new byte[RECORD_SIZE];
        customerFile.readFully(data);

        return parseCustomerData(data);
    }

    private Customer parseCustomerData(byte[] data) {
        Customer customer = new Customer();
        String id = new String(data, 0, 6).trim();
        String name = new String(data, 6, 30).trim();
        String address = new String(data, 36, 30).trim();
        String city = new String(data, 66, 20).trim();
        
        customer.setId(id);
        customer.setName(name);
        customer.setAddress(address);
        customer.setCity(city);
        return customer;
    }

    private void displayCustomer(Customer customer) {
        System.out.println("\nCustomer Information:");
        System.out.println("ID: " + customer.getId());
        System.out.println("Name: " + customer.getName());
        System.out.println("Address: " + customer.getAddress());
        System.out.println("City: " + customer.getCity());
    }

    public void closeFile() {
        try {
            if (customerFile != null) {
                customerFile.close();
            }
        } catch (IOException e) {
            System.err.println("Error closing file: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        CustomerMaintenance maintenance = new CustomerMaintenance();
        maintenance.processUserInput();
        maintenance.closeFile();
    }
}

class Customer {
    private String id;
    private String name;
    private String address;
    private String city;

    // Getters and setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
}