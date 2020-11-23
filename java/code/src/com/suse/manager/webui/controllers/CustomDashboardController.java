/**
 * Copyright (c) 2017 SUSE LLC
 *
 * This software is licensed to you under the GNU General Public License,
 * version 2 (GPLv2). There is NO WARRANTY for this software, express or
 * implied, including the implied warranties of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
 * along with this software; if not, see
 * http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
 *
 * Red Hat trademarks are not licensed under GPLv2. No permission is
 * granted to use or replicate Red Hat trademarks that are incorporated
 * in this software or its documentation.
 */
package com.suse.manager.webui.controllers;

import com.redhat.rhn.domain.user.User;
import spark.ModelAndView;
import spark.Request;
import spark.Response;
import spark.template.jade.JadeTemplateEngine;

import java.util.HashMap;
import java.util.Map;

import static com.suse.manager.webui.utils.SparkApplicationHelper.withCsrfToken;
import static com.suse.manager.webui.utils.SparkApplicationHelper.withUser;
import static com.suse.manager.webui.utils.SparkApplicationHelper.withUserPreferences;
import static spark.Spark.get;

/**
 * Controller class providing backend code for the messages page.
 */
public class CustomDashboardController {

    private static final String APPSMITH_URL = "https://suma-testnaica-srv.mgr.suse.de:7443";
    private static final String APPSMITH_APP_ID = "5fb66de596b73361c74a5469/pages/5fb7a1ed24ef10354e304513";

    /**
     * Invoked from Router. Initialize routes for Systems Views.
     *
     * @param jade the Jade engine to use to render the pages
     */
    public static void initRoutes(JadeTemplateEngine jade) {
        get("/manager/dashboard", withUserPreferences(withCsrfToken(withUser(CustomDashboardController::dashboard))),
                jade);
    }

    /**
     * Displays a list of messages.
     *
     * @param request the request object
     * @param response the response object
     * @param user the user object
     * @return the ModelAndView object to render the page
     */
    public static ModelAndView dashboard(Request request, Response response, User user) {
        Map<String, String> model = new HashMap<>();
        model.put("appsmith_url", APPSMITH_URL);
        model.put("appsmith_app_id", APPSMITH_APP_ID);
        return new ModelAndView(model, "templates/dashboard/dashboard.jade");
    }
}
