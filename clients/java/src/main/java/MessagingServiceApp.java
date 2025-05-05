import org.jdbi.v3.core.Jdbi;
import org.jdbi.v3.sqlobject.SqlObjectPlugin;
import org.jdbi.v3.core.statement.Slf4JSqlLogger;

import java.util.List;

public class MessagingServiceApp {
    public static void main(String[] args) {
        String jdbcUrl = "jdbc:arrow-flight-sql://localhost:50051?useEncryption=false";
        String username = "";
        String password = "";

        // Create a Jdbi instance
        Jdbi jdbi = Jdbi.create(jdbcUrl, username, password);
        jdbi.setSqlLogger(new Slf4JSqlLogger());
        jdbi.installPlugin(new SqlObjectPlugin());
        // Obtain a DAO instance
        MessagingServiceDao dao = jdbi.onDemand(MessagingServiceDao.class);

        try {
            List<MessagingServiceAddOn> addOns1 = dao.getMessagingServiceAddOns("account123", "service456");
            System.out.println("Add-ons by account and service:");
            for (MessagingServiceAddOn addOn : addOns1) {
                System.out.println(addOn.getAddOnSid());
            }

            List<MessagingServiceAddOn> addOns2 = dao.getMessagingServiceAddOnByAddOnType("type789", 10);
            System.out.println("\nAdd-ons by add-on type:");
            for (MessagingServiceAddOn addOn : addOns2) {
                System.out.println(addOn.getAddOnSid());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}