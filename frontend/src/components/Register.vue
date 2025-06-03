<template>
  <div class="register-form">
    <h2>Register</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>Email:</label>
        <input 
          type="email" 
          v-model="formData.email" 
          required
        />
      </div>
      
      <div class="form-group">
        <label>Password:</label>
        <input 
          type="password" 
          v-model="formData.password" 
          required
        />
      </div>

      <div class="form-group">
        <label>Role:</label>
        <select v-model="formData.role" required>
          <option value="merchant">Merchant</option>
          <option value="admin">Administrator</option>
        </select>
      </div>

      <div class="form-group" v-if="formData.role === 'merchant'">
        <label>Business Name:</label>
        <input 
          type="text" 
          v-model="formData.business_name"
        />
      </div>

      <div class="form-group">
        <label>First Name:</label>
        <input 
          type="text" 
          v-model="formData.first_name"
        />
      </div>

      <div class="form-group">
        <label>Last Name:</label>
        <input 
          type="text" 
          v-model="formData.last_name"
        />
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Loading...' : 'Register' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref } from 'vue';
import authService, { RegisterData } from '../services/auth';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'RegisterComponent',
  setup() {
    const router = useRouter();
    const formData = reactive<RegisterData>({
      email: '',
      password: '',
      role: 'merchant',
      business_name: '',
      first_name: '',
      last_name: ''
    });
    const error = ref('');
    const loading = ref(false);

    const handleSubmit = async () => {
      loading.value = true;
      error.value = '';
      
      try {
        await authService.register(formData);
        router.push('/dashboard');
      } catch (err: any) {
        error.value = err.response?.data?.error || 'An error occurred';
      } finally {
        loading.value = false;
      }
    };

    return {
      formData,
      error,
      loading,
      handleSubmit
    };
  }
});
</script>

<style scoped>
.register-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input, select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>