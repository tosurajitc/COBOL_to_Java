package com.company.module;

public class Customer {
    private String id;
    private String name;
    private String address;
    private String city;
    private String state;
    private String zip;
    private String phone;
    private double balance;
    private double creditLimit;
    private String lastOrderDate;

    // Getters and Setters
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
    public double getBalance() { return balance; }
    public void setBalance(double balance) { this.balance = balance; }
    public double getCreditLimit() { return creditLimit; }
    public void setCreditLimit(double creditLimit) { this.creditLimit = creditLimit; }
    public String getLastOrderDate() { return lastOrderDate; }
    public void setLastOrderDate(String lastOrderDate) { this.lastOrderDate = lastOrderDate; }

    @Override
    public String toString() {
        return "Customer{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", address='" + address + '\'' +
                ", city='" + city + '\'' +
                ", state='" + state + '\'' +
                ", zip='" + zip + '\'' +
                ", phone='" + phone + '\'' +
                ", balance=" + balance +
                ", creditLimit=" + creditLimit +
                ", lastOrderDate='" + lastOrderDate + '\'' +
                '}';
    }
}