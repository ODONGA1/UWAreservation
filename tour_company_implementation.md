# Tour Company Implementation Guide

This document provides guidance on the implementation of the new Tour Company affiliation system in the UWA Reservation application.

## Overview

The new system allows tours to be associated with specific tour operators or UWA itself. This implementation follows a multi-tenant approach where:

1. Each tour has a company affiliation
2. Tour operators are linked to their respective companies
3. UWA staff can manage all tours, but tour operators can only manage their own tours
4. Tour visibility and management permissions are based on company affiliations

## Model Structure

The implementation includes:

1. **TourCompany Model**:
   - Represents a tour operator company or UWA itself
   - Has fields for name, description, website, contact info
   - Has a special flag `is_uwa` for UWA-affiliated tours
   - Contains a many-to-many relationship with users who can operate as this company

2. **Updated Tour Model**:
   - Added foreign key to TourCompany
   - Added created_by field to track the user who created the tour
   - Added timestamp fields for created_at and updated_at
   - Added helper methods for company affiliation info

## Setup Instructions

### 1. Run Migrations

Apply the database migrations to create the new tables and fields:

```bash
python manage.py migrate
```

### 2. Initialize Tour Companies

Run the management command to create initial company data:

```bash
python manage.py setup_tour_companies
```

This will:
- Create the default UWA company
- Create companies for existing operators based on their profile data
- Associate existing tours with UWA by default

### 3. Update Tour Forms

The Tour form now requires a company selection:
- UWA staff can select any company
- Tour operators can only select their own companies

### 4. User Permissions

User permissions now work as follows:
- **UWA Staff**: Can create/edit tours for any company
- **Tour Operators**: Can only create/edit tours for their affiliated company
- **Tourists**: Can view tour details including company information

## Testing the Implementation

To test the new functionality:

1. Log in as a UWA staff member and create tours for different companies
2. Log in as a tour operator and verify they can only create/edit their company's tours
3. View the tour detail page to ensure company information is displayed
4. Check the tour management page filters and company dropdown

## Future Enhancements

Consider these potential improvements:
- Add company logos and more detailed company profiles
- Implement company-specific analytics and reports
- Add company-level settings and preferences
- Implement company verification and approval workflows
