package com.cobol.java_conversion;

import java.io.RandomAccessFile;
import java.io.IOException;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class CustomerMaintenance {
    private static final String CUSTOMER_FILE = "custfile.dat";
    private static final int ID_LENGTH = 6;
    private static final int NAME_LENGTH = 30;
    private static final int ADDR_LENGTH = 30;
    private static final int CITY_LENGTH = 20;
    private static final int STATE_LENGTH = 2;
    private static final int ZIP_LENGTH = 5;
    private static final int PHONE_LENGTH = 10;

    private RandomAccessFile customerFile;
    private Scanner scanner;

    public CustomerMaintenance() {
        try {
            customerFile = new RandomAccessFile(CUSTOMER_FILE, "r");
            scanner = new Scanner(System.in);
        } catch (FileNotFoundException e) {
            handleFileError(e, "Customer file not found.");
        }
    }

    public void processCustomerMaintenance() {
        boolean running = true;
        while (running) {
            System.out.print("Enter customer ID (or 'X' to exit): ");
            String input = scanner.next().toUpperCase();
            if (input.equals("X")) {
                running = false;
            } else {
                Customer customer = readCustomer(input);
                if (customer != null) {
                    displayCustomer(customer);
                } else {
                    System.out.println("Customer not found.");
                }
            }
        }
        closeResources();
    }

    private Customer readCustomer(String id) {
        try {
            int recordLength = ID_LENGTH + NAME_LENGTH + ADDR_LENGTH + CITY_LENGTH + STATE_LENGTH + ZIP_LENGTH + PHONE_LENGTH;
            int recordStart = (Integer.parseInt(id) - 1) * recordLength;
            customerFile.seek(recordStart);
            byte[] data = new byte[recordLength];
            customerFile.readFully(data);
            return parseCustomerData(data);
        } catch (IOException e) {
            handleFileError(e, "Error reading customer record.");
            return null;
        }
    }

    private Customer parseCustomerData(byte[] data) {
        Customer customer = new Customer();
        int pos = 0;

        customer.setId(new String(data, pos, ID_LENGTH).trim());
        pos += ID_LENGTH;

        customer.setName(new String(data, pos, NAME_LENGTH).trim());
        pos += NAME_LENGTH;

        customer.setAddress(new String(data, pos, ADDR_LENGTH).trim());
        pos += ADDR_LENGTH;

        customer.setCity(new String(data, pos, CITY_LENGTH).trim());
        pos += CITY_LENGTH;

        customer.setState(new String(data, pos, STATE_LENGTH).trim());
        pos += STATE_LENGTH;

        customer.setZip(new String(data, pos, ZIP_LENGTH).trim());
        pos += ZIP_LENGTH;

        customer.setPhone(new String(data, pos, PHONE_LENGTH).trim());

        return customer;
    }

    private void displayCustomer(Customer customer) {
        System.out.println("Customer ID: " + customer.getId());
        System.out.println("Name: " + customer.getName());
        System.out.println("Address: " + customer.getAddress());
        System.out.println("City: " + customer.getCity());
        System.out.println("State: " + customer.getState());
        System.out.println("Zip: " + customer.getZip());
        System.out.println("Phone: " + customer.getPhone());
    }

    private void handleFileError(IOException e, String message) {
        System.out.println(message);
        System.out.println("Error: " + e.getMessage());
        closeResources();
        System.exit(1);
    }

    private void closeResources() {
        try {
            if (scanner != null) {
                scanner.close();
            }
            if (customerFile != null) {
                customerFile.close();
            }
        } catch (IOException e) {
            System.out.println("Error closing resources: " + e.getMessage());
        }
    }

    public static class Customer {
        private String id;
        private String name;
        private String address;
        private String city;
        private String state;
        private String zip;
        private String phone;

        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getAddress() { return address; }
        public void setAddress(String address) { this.address = address; }
        public String getCity() { return city; }
        public void setCity(String city) { this.city = city; }
        public String getState() { return state; }
        public void setState(String state) { this.state = state; }
        public String getZip() { return zip; }
        public void setZip(String zip) { this.zip = zip; }
        public String getPhone() { return phone; }
        public void setPhone(String phone) { this.phone = phone; }
    }

    public static void main(String[] args) {
        CustomerMaintenance maintenance = new CustomerMaintenance();
        maintenance.processCustomerMaintenance();
    }
}