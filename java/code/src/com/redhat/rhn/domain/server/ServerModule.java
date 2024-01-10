package com.redhat.rhn.domain.server;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.ManyToOne;
import javax.persistence.SequenceGenerator;
import javax.persistence.Table;

@Entity
@Table(name = "suseServerModule")
public class ServerModule {
    // TODO: Consider multi-org scenarios
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "appstreams_servermodule_seq")
    @SequenceGenerator(name = "appstreams_servermodule_seq", sequenceName = "suse_as_servermodule_seq",
            allocationSize = 1)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String stream;

    @Column(nullable = false)
    private String version;

    @Column(nullable = false)
    private String context;

    @Column(nullable = false)
    private String arch;

    @ManyToOne
    @JoinColumn(name = "server_id", nullable = false)
    private Server server;

    public ServerModule() { }

    public ServerModule(String nsvca) {
        String[] items = nsvca.split(":");

        if (items.length != 5) {
            throw new RuntimeException("Malformed NSVCA for module: " + nsvca);
        }

        this.setName(items[0]);
        this.setStream(items[1]);
        this.setVersion(items[2]);
        this.setContext(items[3]);
        this.setArch(items[4]);
    }

    public Long getId() {
        return id;
    }

    public void setId(Long idIn) {
        id = idIn;
    }

    public String getName() {
        return name;
    }

    public void setName(String nameIn) {
        name = nameIn;
    }

    public String getStream() {
        return stream;
    }

    public void setStream(String streamIn) {
        stream = streamIn;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String versionIn) {
        version = versionIn;
    }

    public String getContext() {
        return context;
    }

    public void setContext(String contextIn) {
        context = contextIn;
    }

    public String getArch() {
        return arch;
    }

    public void setArch(String archIn) {
        arch = archIn;
    }

    public Server getServer() {
        return server;
    }

    public void setServer(Server serverIn) {
        server = serverIn;
    }
}
