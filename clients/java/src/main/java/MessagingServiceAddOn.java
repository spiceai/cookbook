import java.sql.Timestamp;

public class MessagingServiceAddOn {
    private String accountSid;
    private String messagingServiceSid;
    private String addOnSid;
    private String addOnTypeSid;
    private String addOnJson;
    private Timestamp dateCreated;
    private Timestamp dateUpdated;

    // Getters and setters
    public String getAccountSid() {
        return accountSid;
    }

    public void setAccountSid(String accountSid) {
        this.accountSid = accountSid;
    }

    public String getMessagingServiceSid() {
        return messagingServiceSid;
    }

    public void setMessagingServiceSid(String messagingServiceSid) {
        this.messagingServiceSid = messagingServiceSid;
    }

    public String getAddOnSid() {
        return addOnSid;
    }

    public void setAddOnSid(String addOnSid) {
        this.addOnSid = addOnSid;
    }

    public String getAddOnTypeSid() {
        return addOnTypeSid;
    }

    public void setAddOnTypeSid(String addOnTypeSid) {
        this.addOnTypeSid = addOnTypeSid;
    }

    public String getAddOnJson() {
        return addOnJson;
    }

    public void setAddOnJson(String addOnJson) {
        this.addOnJson = addOnJson;
    }

    public Timestamp getDateCreated() {
        return dateCreated;
    }

    public void setDateCreated(Timestamp dateCreated) {
        this.dateCreated = dateCreated;
    }

    public Timestamp getDateUpdated() {
        return dateUpdated;
    }

    public void setDateUpdated(Timestamp dateUpdated) {
        this.dateUpdated = dateUpdated;
    }

    @Override
    public String toString() {
        return "MessagingServiceAddOn{" +
                "accountSid='" + accountSid + '\'' +
                ", messagingServiceSid='" + messagingServiceSid + '\'' +
                ", addOnSid='" + addOnSid + '\'' +
                ", addOnTypeSid='" + addOnTypeSid + '\'' +
                ", addOnJson='" + addOnJson + '\'' +
                ", dateCreated=" + dateCreated +
                ", dateUpdated=" + dateUpdated +
                '}';
    }
}
