---
name: android-development
description: 当需要开发Android原生应用、使用Kotlin/Java开发Android、编写Android Activity/Fragment、实现Android UI界面时调用此技能。触发词：Android开发、Android原生、Kotlin Android、Java Android、Activity、Fragment、Android UI、Gradle、Android Studio、Jetpack。
---

# Android 原生开发

## 核心能力

**Android原生应用开发、Kotlin/Java编程、Jetpack组件使用。**

---

## 适用场景

- Android 原生应用开发
- Kotlin/Java 编程
- Jetpack 组件使用
- Material Design 实现

---

## 项目结构

```
app/
├── src/main/
│   ├── java/                    # Java/Kotlin 源码
│   │   └── com/example/app/
│   │       ├── MainActivity.kt
│   │       ├── ui/
│   │       │   ├── screens/
│   │       │   └── components/
│   │       ├── data/
│   │       │   ├── model/
│   │       │   ├── repository/
│   │       │   └── remote/
│   │       └── utils/
│   ├── res/                     # 资源文件
│   │   ├── layout/              # 布局
│   │   ├── drawable/            # 图片
│   │   ├── values/              # 字符串/样式
│   │   └── mipmap/              # 图标
│   └── AndroidManifest.xml
├── build.gradle                 # 构建配置
└── proguard-rules.pro          # 混淆规则
```

---

## Kotlin 基础

### Activity

```kotlin
class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // 初始化视图
        binding.textView.text = "Hello Android"
        binding.button.setOnClickListener {
            // 点击事件
        }
    }
}
```

### Fragment

```kotlin
class HomeFragment : Fragment() {
    
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // 初始化
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
```

---

## Jetpack 组件

### ViewModel

```kotlin
class MainViewModel : ViewModel() {
    private val _data = MutableLiveData<String>()
    val data: LiveData<String> = _data
    
    fun loadData() {
        viewModelScope.launch {
            _data.value = repository.getData()
        }
    }
}

// 使用
class MainActivity : AppCompatActivity() {
    private val viewModel: MainViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        viewModel.data.observe(this) { data ->
            // 更新UI
        }
    }
}
```

### Room 数据库

```kotlin
// Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Int,
    @ColumnInfo(name = "name") val name: String
)

// DAO
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAll(): List<User>
    
    @Insert
    suspend fun insert(user: User)
    
    @Delete
    suspend fun delete(user: User)
}

// Database
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

### Retrofit 网络请求

```kotlin
interface ApiService {
    @GET("users")
    suspend fun getUsers(): List<User>
    
    @POST("users")
    suspend fun createUser(@Body user: User): User
}

// 使用
object RetrofitClient {
    private const val BASE_URL = "https://api.example.com/"
    
    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
```

---

## Compose UI

### 基础组件

```kotlin
@Composable
fun Greeting(name: String) {
    Text(text = "Hello $name!")
}

@Composable
fun MyScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Title",
            style = MaterialTheme.typography.h4
        )
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = { /* 点击 */ }) {
            Text("Click Me")
        }
    }
}
```

### 列表

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(users) { user ->
            UserItem(user = user)
        }
    }
}

@Composable
fun UserItem(user: User) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Row(modifier = Modifier.padding(16.dp)) {
            Text(text = user.name)
        }
    }
}
```

---

## Gradle 配置

```groovy
// build.gradle (app level)
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
    id 'kotlin-kapt'
}

android {
    namespace 'com.example.app'
    compileSdk 34
    
    defaultConfig {
        applicationId "com.example.app"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }
    
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    
    composeOptions {
        kotlinCompilerExtensionVersion '1.5.0'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'
    implementation 'androidx.activity:activity-compose:1.8.2'
    
    // Compose
    implementation platform('androidx.compose:compose-bom:2024.01.00')
    implementation 'androidx.compose.ui:ui'
    implementation 'androidx.compose.material3:material3'
}
```

---

## 常用命令

```bash
# 构建
./gradlew assembleDebug
./gradlew assembleRelease

# 清理
./gradlew clean

# 运行测试
./gradlew test

# 安装到设备
adb install app-debug.apk

# 查看日志
adb logcat
```

---

## 注意事项

```
必须:
- 使用Kotlin优先
- 遵循Material Design
- 处理生命周期
- 适配不同屏幕尺寸

避免:
- 主线程执行耗时操作
- 内存泄漏
- 硬编码尺寸
- 忽略返回键处理
```

---

## 相关技能

- `kotlin-android` - Kotlin Android开发
- `flutter-development` - Flutter跨平台
- `mobile-performance` - 移动端性能优化