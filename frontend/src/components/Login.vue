<template>
  <div class="login-form">
    <h2>Login</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>Email:</label>
        <input 
          type="email" 
          v-model="email" 
          required
        />
      </div>
      
      <div class="form-group">
        <label>Password:</label>
        <input 
          type="password" 
          v-model="password" 
          required
        />
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Loading...' : 'Login' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import authService from '../services/auth';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'LoginComponent',
  setup() {
    const router = useRouter();
    const email = ref('');
    const password = ref('');
    const error = ref('');
    const loading = ref(false);

    const handleSubmit = async () => {
      loading.value = true;
      error.value = '';
      
      try {
        await authService.login({
          email: email.value,
          password: password.value
        });
        router.push('/dashboard');
      } catch (err: any) {
        error.value = err.response?.data?.error || 'An error occurred';
      } finally {
        loading.value = false;
      }
    };

    return {
      email,
      password,
      error,
      loading,
      handleSubmit
    };
  }
});
</script>

<style scoped>
.login-form {
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

input {
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