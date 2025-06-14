interface registerMerchantPayload {
    business_name: string;
    registration_number: string;
    contact_email: string;
    contact_phone: string;
    admin_name: string;
    admin_email: string;
    password: string;
    confirm_password: string;
}

async function registerMerchant(payload: registerMerchantPayload): Promise<any> {
    try {
        const response = await axios.post("/merchant/register/", payload);
        return response.data;
    } catch (error) {
        console.error("Error registering merchant:", error);
        throw error;
    }
}


async function getDashboard() {
    const res = await axios.get("/merchant/dashboard/")
        .then(res => res.data)
        .catch(error => {
            console.error("Error fetching dashboard data:", error);
            throw error;
        }
}

async function getTransactions() {
    return axios.get("/merchant/transactions/")
        .then(res => res.data)
        .catch(error => {
            console.error("Error fetching transactions:", error);
            throw error;
        });
}

async function recievePayment() {

}

async function generateApiCredentials() {
    return axios.get("/merchant/generate_api_credentials/")
        .then(res => res.data)
        .catch(error => {
            console.error("Error generating API credentials:", error);
            throw error;
        });
}

export const merchant = { registerMerchant, getDashboard, getTransactions, recievePayment, generateApiCredentials };
