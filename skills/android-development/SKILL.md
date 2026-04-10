---
name: android-development
description: Android原生应用开发、Kotlin/Java编程、Jetpack组件使用。
---

# Android 原生开发

## 核心能力

Android原生应用开发、Kotlin/Java编程、Jetpack组件使用。

## 项目结构

```
app/src/main/
├── java/com/example/app/    # 源码
├── res/                     # 资源
└── AndroidManifest.xml
```

## Kotlin 基础

### Activity

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
    }
}
```

### Fragment

```kotlin
class HomeFragment : Fragment() {
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
```

## Jetpack 组件

### ViewModel

```kotlin
class MainViewModel : ViewModel() {
    private val _data = MutableLiveData<String>()
    val data: LiveData<String> = _data
}
```

### Room 数据库

```kotlin
@Entity(tableName = "users")
data class User(@PrimaryKey val id: Int, @ColumnInfo(name = "name") val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM users") suspend fun getAll(): List<User>
    @Insert suspend fun insert(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

### Retrofit 网络请求

```kotlin
interface ApiService {
    @GET("users") suspend fun getUsers(): List<User>
    @POST("users") suspend fun createUser(@Body user: User): User
}
```

## Compose UI

```kotlin
@Composable
fun MyScreen() {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Title", style = MaterialTheme.typography.h4)
        Button(onClick = { }) { Text("Click Me") }
    }
}
```

## 常用命令

```bash
./gradlew assembleDebug    # 构建
./gradlew clean           # 清理
adb install app-debug.apk # 安装
adb logcat                # 查看日志
```

## 注意事项

- 使用Kotlin优先
- 遵循Material Design
- 处理生命周期
- 避免主线程耗时操作
- 防止内存泄漏
