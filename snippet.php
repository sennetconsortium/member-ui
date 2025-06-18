// Register the metabox and fields.
add_action( 'cn_metabox', 'cn_register_custom_metabox_and_text_field' );
 
function cn_register_custom_metabox_and_text_field() {
    // Award/component
    $component_atts = array(
        'title'    => 'SenNet Award/component', // Change this to a name which applies to your project.
        'id'       => 'sn_component', // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Award/component',     // Change this field name to something which applies to you project.
                'show_label' => TRUE,             // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_component', // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'select',  // This is the field type being added.
                'options'    => array(
                    '' => '',
                    'Consortium Organization and Data Coordinating Center (CODCC)' => 'Consortium Organization and Data Coordinating Center (CODCC)',
                    'National Institutes of Health (NIH)' => 'National Institutes of Health (NIH)',
                    'TDA - Buck Institute for Research on Aging'   => 'TDA - Buck Institute for Research on Aging',
                    'TDA - Brown University'   => 'TDA - Brown University',
                    'TDA - Columbia University'   => 'TDA - Columbia University',
                    'TDA - Johns Hopkins University'   => 'TDA - Johns Hopkins University',
                    'TDA - Massachusetts General Hospital' => 'TDA - Massachusetts General Hospital',
                    'TDA - Massachusetts Institute of Technology' => 'TDA - Massachusetts Institute of Technology',
                    'TDA - Mayo Clinic - Passos'  => 'TDA - Mayo Clinic - Passos',
                    'TDA - Mayo Clinic - Schafer'  => 'TDA - Mayo Clinic - Schafer',
                    'TDA - Pacific Northwest National Laboratory'   => 'TDA - Pacific Northwest National Laboratory',
                    'TDA - Stanford University'  => 'TDA - Stanford University',
                    'TDA - University of Michigan' => 'TDA - University of Michigan',
                    'TDA - University of Washington' => 'TDA - University of Washington',
                    'TMC - Buck Institute for Research on Aging' => 'TMC - Buck Institute for Research on Aging',
                    'TMC - Columbia University Irving Medical Center' => 'TMC - Columbia University Irving Medical Center',
                    'TMC - Johns Hopkins University'   => 'TMC - Johns Hopkins University',
                    'TMC - UConn Health' => 'TMC - UConn Health',
                    'TMC - University of California San Diego' => 'TMC - University of California San Diego',
                    'TMC - University of Minnesota - Robbins' => 'TMC - University of Minnesota - Robbins',
                    'TMC - University of Minnesota - Niedernhofer' => 'TMC - University of Minnesota - Niedernhofer',
                    'TMC - University of Pittsburgh' => 'TMC - University of Pittsburgh',
                    "TMC - Washington University in St. Louis" => "TMC - Washington University in St. Louis",
                    'TMC - Yale University - Fan' => 'TMC - Yale University - Fan',
                    'TMC - Yale University - Dixit' => 'TMC - Yale University - Dixit'
                ),
                'default'    => '', // This is the default selected option. Leave blank for none.
            ),
        ),
    );

    $other_component_atts = array(
        'title'    => 'Other Component',         // Change this to a name which applies to your project.
        'id'       => 'sn_other_component',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Other component', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_other_component',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );

    // Organization
    $organization_atts = array(
        'title'    => 'Organization', // Change this to a name which applies to your project.
        'id'       => 'sn_organization', // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Organization',     // Change this field name to something which applies to you project.
                'show_label' => TRUE,             // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_organization', // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'select',  // This is the field type being added.
                'options'    => array(
                    '' => '',
                    'Buck Institute for Research on Aging' => 'Buck Institute for Research on Aging',
                    'Brown University' => 'Brown University',
                    'Columbia University' => 'Columbia University',
                    'Carnegie Mellon University (CMU)' => 'Carnegie Mellon University (CMU)',
                    'Columbia University Irving Medical Center' => 'Columbia University Irving Medical Center',
                    'Department of Biomedical Informatics (DBMI)/Unversity of Pittsburgh(Pitt)' => 'Department of Biomedical Informatics (DBMI)/Unversity of Pittsburgh(Pitt)',
                    'EMBL-EBI' => 'EMBL-EBI',
                    'Harvard Medical School' => 'Harvard Medical School',
                    'Harvard University' => 'Harvard University',
                    'Indiana University' => 'Indiana University',
                    'Johns Hopkins University' => 'Johns Hopkins University',
                    'La Jolla Institute for Immunology' => 'La Jolla Institute for Immunology',
                    'Massachusetts General Hospital' => 'Massachusetts General Hospital',
                    'Mayo Clinic' => 'Mayo Clinic',
                    'Massachusetts Institute of Technology' => 'Massachusetts Institute of Technology',
                    'National Institutes of Health (NIH)' => 'National Institutes of Health (NIH)',
                    'New York Genome Center' => 'New York Genome Center',
                    'Northeastern University' => 'Northeastern University',
                    'Northwestern University' => 'Northwestern University',
                    'The Ohio State University' => 'The Ohio State University',
                    'Pacific Northwest National Laboratory' => 'Pacific Northwest National Laboratory',
                    'Pittsburgh Supercomputing Center (PSC)' => 'Pittsburgh Supercomputing Center (PSC)',
                    'Sanford Burnham Prebys Medical Discovery Institute' => 'Sanford Burnham Prebys Medical Discovery Institute',
                    'Stanford University' => 'Stanford University',
                    'The Jackson Laboratory' => 'The Jackson Laboratory',
                    'The Jackson Laboratory for Genomic Medicine' => 'The Jackson Laboratory for Genomic Medicine',
                    'UConn Health' => 'UConn Health',
                    'University of Connecticut' => 'University of Connecticut',
                    'University of California San Diego' => 'University of California San Diego',
                    'University of Michigan' => 'University of Michigan',
                    'University of Minnesota' => 'University of Minnesota',
                    'University of Texas Health Science Center at San Antonio (UTHSCSA)' => 'University of Texas Health Science Center at San Antonio (UTHSCSA)',
                    'University of Pittsburgh' => 'University of Pittsburgh',
                    'University of Washington' => 'University of Washington',
                    'Wake Forest University' => 'Wake Forest University',
                    'Washington University in St. Louis' => 'Washington University in St. Louis',
                    'Yale School of Medicine' => 'Yale School of Medicine',
                    'Yale University' => 'Yale University',
                    'Other' => 'Other'
                ),
                'default'    => '', // This is the default selected option. Leave blank for none.
            ),
        ),
    );

    $other_organization_atts = array(
        'title'    => 'Other Organization',         // Change this to a name which applies to your project.
        'id'       => 'sn_other_organization',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Other organization', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_other_organization',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );

    // Role
    $role_atts = array(
        'title'    => 'Role in SenNet', // Change this to a name which applies to your project.
        'id'       => 'sn_role', // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Role',     // Change this field name to something which applies to you project.
                'show_label' => TRUE,             // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_role', // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'select',  // This is the field type being added.
                'options'    => array(
                    '' => '',
                    'Administrative Assistant'   => 'Administrative Assistant',
                    'Agreement Specialist'   => 'Agreement Specialist',
                    'Associate Member' => 'Associate Member',
                    'Chief Scientist' => 'Chief Scientist',
                    'Co-Investigator' => 'Co-Investigator',
                    'Compliance Officer'  => 'Compliance Officer',
                    'Computer Scientist'  => 'Computer Scientist',
                    'CUSP'  => 'CUSP',
                    'Data Analysis Core' => 'Data Analysis Core',
                    'Data Architect' => 'Data Architect',
                    'Data Curator' => 'Data Curator',
                    'Data Manager' => 'Data Manager',
                    'Data Scientist' => 'Data Scientist',
                    'Designer' => 'Designer',
                    'External Program Consultant' => 'External Program Consultant',
                    'Graduate Student' => 'Graduate Student',
                    'Image Scientist' => 'Image Scientist',
                    'Informatics' => 'Informatics',
                    'Lead Software Developer' => 'Lead Software Developer',
                    'ML Scientist' => 'ML Scientist',
                    'Meeting Facilitator' => 'Meeting Facilitator',
                    'Network Support' => 'Network Support',
                    'PI' => 'PI',
                    'PI (Contact)' => 'PI (Contact)',
                    'Pathology Assessment' => 'Pathology Assessment',
                    'Postdoctoral Fellow' => 'Postdoctoral Fellow',
                    'Program Coordinator' => 'Program Coordinator',
                    'Program Officer' => 'Program Officer',
                    'Program Manager' => 'Program Manager',
                    'Project Scientist' => 'Project Scientist',
                    'Researcher' => 'Researcher',
                    'Scientific Program Manager' => 'Scientific Program Manager',
                    'Software Developer' => 'Software Developer',
                    'Software Engineer' => 'Software Engineer',
                    'System Support' => 'System Support',
                    'Team Leader' => 'Team Leader',
                    'WG Member' => 'WG Member',
                    'Website Developer' => 'Website Developer',
                    'Other' => 'Other'
                ),
                'default'    => '', // This is the default selected option. Leave blank for none.
            ),
        ),
    );

    $other_role_atts = array(
        'title'    => 'Other Role',         // Change this to a name which applies to your project.
        'id'       => 'sn_other_role',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Other role', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_other_role',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );

    $ar_atts = array(
        'title'    => 'Which SenNet resources will you need to access?', // Change this to a name which applies to your project.
        'id'       => 'sn_access_requests', // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Access request',     // Change this field name to something which applies to you project.
                'show_label' => TRUE,             // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_access_requests', // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'checkboxgroup',  // This is the field type being added.
                'options'    => array(
                    'SenNet Data Via Globus'   => 'SenNet Data Via Globus',
                    'Member Portal' => 'Member Portal',
                    'protocols.io'   => 'protocols.io',
                    'SenNet Google Drive Share'  => 'SenNet Google Drive Share',
                    'SenNet GitHub Repository'  => 'SenNet GitHub Repository',
                    'SenNet Slack Workspace' => 'SenNet Slack Workspace'
                ),
                'default'    => '', // This is the default selected option. Leave blank for none.
            ),
        ),
    );

    $globus_identity_atts = array(
        'title'    => 'What is your Globus account identity?',         // Change this to a name which applies to your project.
        'id'       => 'sn_globus_identity',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Globus identity', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_globus_identity',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );

    $google_email_atts = array(
        'title'    => 'What email address is linked to your preferred Google account?',         // Change this to a name which applies to your project.
        'id'       => 'sn_google_email',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Google email', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_google_email',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );
    
    $github_username_atts = array(
        'title'    => 'What is your GitHub username?',         // Change this to a name which applies to your project.
        'id'       => 'sn_github_username',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Github username', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_github_username',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );
    
    $slack_username_atts = array(
        'title'    => 'What is your Slack username?',         // Change this to a name which applies to your project.
        'id'       => 'sn_slack_username',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Slack username', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_slack_username',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );

    $protocols_io_email_atts = array(
        'title'    => 'What is your protocols.io account email?',         // Change this to a name which applies to your project.
        'id'       => 'sn_protocols_io_email',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'protocols.io email', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_protocols_io_email',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );
    
    $website_atts = array(
        'title'    => 'Personal Website',         // Change this to a name which applies to your project.
        'id'       => 'sn_website',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Personal website', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_website',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );

    $orcid_atts = array(
        'title'    => 'What is your ORCID ID?',         // Change this to a name which applies to your project.
        'id'       => 'sn_orcid',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'ORCID ID', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_orcid',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );
    
    $pm_atts = array(
        'title'    => 'Is there a project manager who should be copied on all communications to you?',         // Change this to a name which applies to your project.
        'id'       => 'sn_pm',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Project manager', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_pm',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'radio',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
                'options'    => array(
                    '1'   => 'Yes',
                    '0'   => 'No',
                ),
            ),
        ),
    );
    
    $pm_name_atts = array(
        'title'    => 'Project Manager\'s name',         // Change this to a name which applies to your project.
        'id'       => 'sn_pm_name',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Project manager name', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_pm_name',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );
    
    $pm_email_atts = array(
        'title'    => 'Project Manager\'s email',         // Change this to a name which applies to your project.
        'id'       => 'sn_pm_email',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'Project manager email', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_pm_email',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );

    $globus_parsed_email_atts = array(
        'title'    => 'What email address is linked to your Globus Login account?',         // Change this to a name which applies to your project.
        'id'       => 'sn_globus_parsed_email',           // Change this so it is unique to you project.
        'context'  => 'normal',
        'priority' => 'core',
        'fields'   => array(
            array(
                'name'       => 'globus email', // Change this field name to something which applies to you project.
                'show_label' => TRUE,         // Whether or not to display the 'name'. Changing it to false will suppress the name.
                'id'         => 'sn_globus_parsed_email',   // Change this so it is unique to you project. Each field id MUST be unique.
                'type'       => 'text',       // This is the field type being added.
                'size'       => 'regular',    // This can be changed to one of the following: 'small', 'regular', 'large'
            ),
        ),
    );

 
    cnMetaboxAPI::add( $component_atts );
    cnMetaboxAPI::add( $other_component_atts);
    cnMetaboxAPI::add( $organization_atts );
    cnMetaboxAPI::add( $other_organization_atts);
    cnMetaboxAPI::add( $role_atts );
    cnMetaboxAPI::add( $other_role_atts);
    cnMetaboxAPI::add( $ar_atts );
    cnMetaboxAPI::add( $globus_identity_atts);
    cnMetaboxAPI::add( $google_email_atts);
    cnMetaboxAPI::add( $github_username_atts);
    cnMetaboxAPI::add( $slack_username_atts);
    cnMetaboxAPI::add( $protocols_io_email_atts);
    cnMetaboxAPI::add( $website_atts );
    cnMetaboxAPI::add( $orcid_atts );
    cnMetaboxAPI::add( $pm_atts );
    cnMetaboxAPI::add( $pm_name_atts );
    cnMetaboxAPI::add( $pm_email_atts );
    cnMetaboxAPI::add( $globus_parsed_email_atts);
}
