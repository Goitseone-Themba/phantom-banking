import axios from "axios";

async function registerCustomer(payload) {
    try {
        const response = await axios.post("/customer/register/", payload);
        return response.data;
    } catch (error) {
        console.error("Error registering customer:", error);
        throw error;
    }
}

async function getTransactions() {
    try {
        const response = await axios.get("/customer/transactions/");
        return response.data;
    } catch (error) {
        console.error("Error fetching customer transactions:", error);
        throw error;
    }
}
export const customer = {}
