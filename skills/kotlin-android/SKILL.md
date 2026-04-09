---
name: kotlin-android
description: 当需要使用Kotlin开发Android应用、编写Kotlin Android代码、使用Kotlin协程和扩展函数时调用此技能。触发词：Kotlin Android、Kotlin开发、Kotlin协程、Kotlin扩展函数、Android Kotlin、Jetpack Compose Kotlin。
---

# Kotlin Android 开发

## 核心能力

**Kotlin语言特性、Android开发实践、协程与Flow。**

---

## 适用场景

- Kotlin Android 开发
- 协程异步处理
- 扩展函数编写
- Jetpack Compose

---

## Kotlin 基础

### 变量与函数

```kotlin
// 变量
val name = "张三"        // 不可变
var age = 25            // 可变

// 函数
fun add(a: Int, b: Int): Int {
    return a + b
}

// 单表达式函数
fun add(a: Int, b: Int) = a + b

// 默认参数
fun greet(name: String = "World") {
    println("Hello, $name")
}

// 扩展函数
fun String.isEmail(): Boolean {
    return this.contains("@")
}

// 使用
"test@example.com".isEmail()
```

### 数据类

```kotlin
data class User(
    val id: Int,
    val name: String,
    val email: String? = null
)

// 解构
val (id, name) = user

// 复制
val newUser = user.copy(name = "新名字")
```

### 密封类

```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String) : UiState()
}

// 使用
when (state) {
    is UiState.Loading -> { }
    is UiState.Success -> { state.data }
    is UiState.Error -> { state.message }
}
```

---

## 协程

### 基础使用

```kotlin
// 启动协程
viewModelScope.launch {
    val data = repository.getData()
    _state.value = UiState.Success(data)
}

// async/await
viewModelScope.launch {
    val deferred = async {
        repository.getData()
    }
    val data = deferred.await()
}

// 挂起函数
suspend fun fetchData(): List<User> {
    return withContext(Dispatchers.IO) {
        api.getUsers()
    }
}
```

### Flow

```kotlin
// 创建Flow
fun getItems(): Flow<List<Item>> = flow {
    while (true) {
        val items = repository.getItems()
        emit(items)
        delay(5000)  // 每5秒刷新
    }
}

// 收集
viewModelScope.launch {
    repository.getItems()
        .flowOn(Dispatchers.IO)
        .collect { items ->
            _items.value = items
        }
}

// StateFlow
private val _state = MutableStateFlow<UiState>(UiState.Loading)
val state: StateFlow<UiState> = _state.asStateFlow()

// 在UI收集
lifecycleScope.launch {
    viewModel.state.collect { state ->
        // 更新UI
    }
}
```

### 协程异常处理

```kotlin
// CoroutineExceptionHandler
val handler = CoroutineExceptionHandler { _, exception ->
    Log.e("Coroutine", "Error", exception)
}

viewModelScope.launch(handler) {
    // 协程代码
}

// try/catch
viewModelScope.launch {
    try {
        val data = repository.getData()
        _state.value = UiState.Success(data)
    } catch (e: Exception) {
        _state.value = UiState.Error(e.message ?: "未知错误")
    }
}
```

---

## Jetpack Compose

### 可组合函数

```kotlin
@Composable
fun Greeting(name: String) {
    Text(text = "Hello, $name!")
}

@Composable
fun UserCard(user: User) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = user.name,
                style = MaterialTheme.typography.h6
            )
            Text(
                text = user.email,
                style = MaterialTheme.typography.body2
            )
        }
    }
}
```

### 状态管理

```kotlin
// remember
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    
    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("增加")
        }
    }
}

// ViewModel集成
@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val users by viewModel.users.collectAsState()
    
    LazyColumn {
        items(users) { user ->
            UserCard(user = user)
        }
    }
}
```

### 列表

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(8.dp),
        contentPadding = PaddingValues(16.dp)
    ) {
        items(users, key = { it.id }) { user ->
            UserCard(user = user)
        }
    }
}

// Grid
@Composable
fun PhotoGrid(photos: List<Photo>) {
    LazyVerticalGrid(
        columns = GridCells.Fixed(3),
        spacing = 8.dp
    ) {
        items(photos) { photo ->
            PhotoItem(photo)
        }
    }
}
```

### 导航

```kotlin
// NavHost
@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    
    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onNavigate = { navController.navigate("detail/$it") }
            )
        }
        composable(
            "detail/{id}",
            arguments = listOf(navArgument("id") { type = NavType.IntType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getInt("id") ?: 0
            DetailScreen(id = id)
        }
    }
}
```

---

## 常用扩展

### Context扩展

```kotlin
fun Context.showToast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}

fun Context.dpToPx(dp: Int): Int {
    return (dp * resources.displayMetrics.density).toInt()
}

// 使用
context.showToast("成功")
```

### View扩展

```kotlin
fun View.visible() {
    visibility = View.VISIBLE
}

fun View.gone() {
    visibility = View.GONE
}

fun View.onClick(action: () -> Unit) {
    setOnClickListener { action() }
}
```

---

## 注意事项

```
必须:
- 使用协程处理异步
- 遵循MVVM架构
- 使用StateFlow管理状态
- 处理生命周期

避免:
- 内存泄漏
- 主线程网络请求
- 过度使用GlobalScope
- 忽略空安全
```

---

## 相关技能

- `android-development` - Android开发
- `mobile-performance` - 移动端性能
- `mobile-deployment` - 应用发布