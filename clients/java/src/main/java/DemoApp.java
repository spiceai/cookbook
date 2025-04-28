import org.skife.jdbi.v2.sqlobject.{Bind, SqlQuery}
import org.skife.jdbi.v2.sqlobject.stringtemplate.UseStringTemplate3StatementLocator
import org.skife.jdbi.v2.DBI
import java.sql.Timestamp
import java.util.{List => JavaList}

// Case class to map query results
case class ComponentRecord(
  RecordId: String,
  GroupId: String,
  ComponentId: String,
  ComponentTypeId: String,
  ComponentConfig: String,
  CreationTimestamp: Timestamp,
  UpdateTimestamp: Timestamp
)

// DAO interface with the provided SQL queries
@UseStringTemplate3StatementLocator
trait ComponentRecordDao {
  @SqlQuery(
    """
      SELECT RecordId, GroupId, ComponentId, ComponentTypeId, ComponentConfig, CreationTimestamp, UpdateTimestamp
      FROM addons
      WHERE RecordId = :recordId and GroupId = :groupId
      ORDER BY CreationTimestamp DESC
    """
  )
  def getComponentsByRecordAndGroup(
    @Bind("recordId") recordId: String,
    @Bind("groupId") groupId: String
  ): JavaList[ComponentRecord]

  @SqlQuery(
    """
      SELECT RecordId, GroupId, ComponentId, ComponentTypeId, ComponentConfig, CreationTimestamp, UpdateTimestamp
      FROM addons
      WHERE ComponentTypeId = :componentTypeId
      LIMIT :batchSize
    """
  )
  def getComponentsByType(
    @Bind("componentTypeId") componentTypeId: String,
    @Bind("batchSize") batchSize: Int
  ): JavaList[ComponentRecord]
}

object FlightSqlJdbiExample extends App {
  // JDBC URL for Flight SQL (replace with your Flight SQL server details)
  val jdbcUrl = "jdbc:arrow-flight-sql://localhost:31337?useEncryption=false"
  val username = "admin" // Replace with your username
  val password = "password" // Replace with your password

  // Initialize JDBI with Flight SQL JDBC driver
  val dbi = new DBI(jdbcUrl, username, password)

  // Register custom mapper for ComponentRecord
  dbi.registerMapper((rs, ctx) => {
    ComponentRecord(
      RecordId = rs.getString("RecordId"),
      GroupId = rs.getString("GroupId"),
      ComponentId = rs.getString("ComponentId"),
      ComponentTypeId = rs.getString("ComponentTypeId"),
      ComponentConfig = rs.getString("ComponentConfig"),
      CreationTimestamp = rs.getTimestamp("CreationTimestamp"),
      UpdateTimestamp = rs.getTimestamp("UpdateTimestamp")
    )
  })

  try {
    val handle = dbi.open()
    try {
      // Create a DAO instance
      val dao = handle.attach(classOf[ComponentRecordDao])

      // Example 1: Query components by recordId and groupId
      val components = dao.getComponentsByRecordAndGroup(
        recordId = "R123456789",
        groupId = "G987654321"
      )
      println("Components by record and group:")
      components.forEach(component => println(component))

      // Example 2: Query components by componentTypeId with batch size
      val componentsByType = dao.getComponentsByType(
        componentTypeId = "CT123",
        batchSize = 10
      )
      println("\nComponents by component type:")
      componentsByType.forEach(component => println(component))
    } finally {
      handle.close()
    }
  } catch {
    case e: Exception => e.printStackTrace()
  }
}
