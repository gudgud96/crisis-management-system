from SocialMedia import model, renderer, connector

ALERT_AUTHORITY_SPEC = """
Crisis Management System

The following incident was recorded and assistance is required from your department.

*Incident ID*
{0.identifier}

*Reported Time*
{0.reported_time}

*Caller Name* 
{0.name}

*Caller Phone*
{0.phone}

*Address*
{0.address.street_name} {0.address.unit_number}
{0.address.postal_code}

*Description*
{0.description}

*Assistance Required*
{0.assistance_required}

*Priority Values*
Injury: {0.priority.injury}
Danger: {0.priority.danger}
Help:{0.priority.help}
"""

ALERT_PUBLIC_SPEC = """
Public Alert Message
        
This is a public alert message to inform you 
that an incident has occurred on {0.date} {0.time} 
in the vicinity of your residential area, 
please follow the advisory stated below on any possible 
follow-up actions.
        
Incident Name: 
{0.name}

Incident Category: 
{0.category}
        
Description:
{0.description}
        
Advisory:
{0.advisory}
"""


class SocialMedia:
    """
    SocialMedia is the main-entry point for the social media subsystem. It is a controller class that provides the
    following services:
        - Alert authorities about an incident
        - Alert public members residing near a crisis area about a crisis
        - Post to facebook with information about a crisis
    """

    def __init__(self):
        self.alert_authority_renderer = renderer.MessageFormatRenderer(ALERT_AUTHORITY_SPEC)
        self.alert_public_renderer = renderer.MessageFormatRenderer(ALERT_PUBLIC_SPEC)
        self.facebook_renderer = renderer.MessageFormatRenderer(ALERT_PUBLIC_SPEC)

        self.facebook_connector = connector.FacebookConnector()
        self.sms_connector = connector.SMSConnector()

    def alert_authorities(self, incident: model.IncidentReport, authority):
        """
        Alert authorities about an incident
        :param incident: The details of an incident
        :param authority:  Valid values are defined in Model.Contact.AUTHORITY_* constants
        :return: None
        """

        self.sms_connector.send_message(self.alert_authority_renderer.render_message(incident),
                                        model.Contact.retrieve_authority_contact(authority).phone)

    def alert_public(self, crisis: model.CrisisReport, max_distance_km=5):
        """
        Alert public members residing near a crisis area about a crisis
        :param crisis: The details of a crisis
        :param max_distance_km: The maximum distance of nearby residents
        :return: None
        """

        public_members = model.Person.retrieve_nearby_residents(crisis.address.coordinates, max_distance_km)
        for member in public_members:
            self.sms_connector.send_message(self.alert_public_renderer.render_message(crisis), member.phone)

    def post_facebook(self, crisis: model.CrisisReport):
        """
        Post to facebook with information about a crisis
        :param crisis: The details of a crisis
        :return: None
        """

        self.facebook_connector.send_message(self.facebook_renderer.render_message(crisis))
