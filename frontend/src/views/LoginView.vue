<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
      <!-- 显示登入或注册头  -->
      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-gray-900">{{ isLogin ? '登录' : '注册' }}</h2>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm space-y-4">
          <!-- 用户名输入框  -->
          <div>
            <label for="username" class="sr-only">用户名</label>
            <input id="username" v-model="form.username" name="username" type="text" required 
                   class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" 
                   placeholder="用户名" />
          </div>
          <!-- 密码输入框  -->
          <div>
            <label for="password" class="sr-only">密码</label>
            <input id="password" v-model="form.password" name="password" type="password" required 
                   class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" 
                   placeholder="密码" />
          </div>
          <!-- 如果是注册则还需显示确认密码输入框 -->
          <div v-if="!isLogin">
            <label for="confirmPassword" class="sr-only">确认密码</label>
            <input id="confirmPassword" v-model="form.confirmPassword" name="confirmPassword" type="password" 
                   class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" 
                   placeholder="确认密码" />
          </div>
        </div>

        <!--(提交表单)回车按钮-->
        <div>
          <button type="submit" 
                  class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
            {{ isLogin ? '登录' : '注册' }}
          </button>
        </div>
      </form>
      
      <!--切换模式-->
      <div class="text-center mt-4">
        <button @click="toggleMode" class="text-sm text-primary hover:text-primary-dark">
          {{ isLogin ? '没有账号？点击注册' : '已有账号？点击登录' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { login, signup} from '@/api/auth';

const router = useRouter();
const isLogin = ref(true);
const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
});

const toggleMode = () => {
  isLogin.value = !isLogin.value;
  form.username = '';
  form.password = '';
  form.confirmPassword = '';
};

//TO DO
//后续需加await等来实现异步的合理性
const handleSubmit = async () => {
  try {
    if (!isLogin.value && form.password !== form.confirmPassword) {
      alert('两次输入的密码不一致');
      return;
    }
    
    // console.log("提交表单", form);
    // localStorage.setItem('user', JSON.stringify({ account: form.account }));
    // router.push('/dashboard'); // 跳转到课表页面


    let response;
    if (isLogin.value) {
      // 调用后端的登录 API
      response = await login(form.username, form.password);
    } else {
      // 调用后端的注册 API
      response = await signup(form.username, form.password);
    }

    // 判断请求是否成功
    if (response.data.code === 200) {
      alert(isLogin.value ? '登录成功' : '注册成功');
      localStorage.setItem('user', JSON.stringify({ username: form.username }));
      router.push('/dashboard'); // 跳转到课表页面
    } else {
      alert(response.data.msg || '操作失败');
    }
  } catch (error) {
    console.error('登录/注册失败:', error);
    alert('登录/注册失败，请重试');
  }
};
</script>

<style scoped>
.bg-primary {
  background-color: #4f46e5;
}
.bg-primary-dark {
  background-color: #4338ca;
}
.text-primary {
  color: #4f46e5;
}
.text-primary-dark {
  color: #4338ca;
}
.focus\:ring-primary:focus {
  --tw-ring-color: #4f46e5;
}
.focus\:border-primary:focus {
  border-color: #4f46e5;
}
</style>