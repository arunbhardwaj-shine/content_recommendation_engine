pdf_query = """
SELECT 
    p.id AS pdf_id,
    p.file_type,
    p.popup_email_content_language,
    CASE 
        WHEN p.file_type = 'ebook' THEN pf.file_name 
        ELSE p.pdf_file 
    END AS file_name,
    p.tags,
    CASE
        WHEN p.folder_name IS NOT NULL AND p.folder_name != '0' THEN p.folder_name
        ELSE pf.folder_name
    END AS folder_name
FROM pdfs p
LEFT JOIN pdf_files pf 
    ON pf.pdf_id = p.id
WHERE p.uploaded_by IN (22899,29836198,2147494217,2147494218,2147494219,2147498474)
  AND p.file_type IN ('ebook', 'pdf','video')
  AND p.tags IS NOT NULL
  AND p.tags != '[]'
  AND p.tags != '[""]'
  AND p.tags != ''
  AND (p.file_type != 'ebook' OR pf.file_name != '')
    """

user_sequences_query = """
SELECT
    ptt.user_id,
    ptt.pdf_id,
    DATE(ptt.starttime) AS read_date,
    MIN(ptt.starttime) AS starttime
FROM pdf_time_tracks ptt
JOIN pdfs pdf
    ON pdf.id = ptt.pdf_id
WHERE 
    ptt.starttime >= '2000-01-01'
    AND ptt.pdf_id <> 0
    AND pdf.delete_status = 0
    AND pdf.draft = 0
    AND (pdf.exp_datetime IS NULL OR pdf.exp_datetime >= CURRENT_DATE)
    AND EXISTS (
        SELECT 1
        FROM profiles p
        WHERE p.user_id = ptt.user_id
          AND p.user_status = 0
    )
GROUP BY 
    ptt.user_id,
    ptt.pdf_id,
    YEAR(ptt.starttime),
    MONTH(ptt.starttime),
    DAY(ptt.starttime)
ORDER BY starttime ASC;
"""

docintel_query = """
SELECT
    folder_name,
    code,
    ibu
    from pdfs WHERE id = :pdf_id
    LIMIT 1
"""

pdf_file_lookup_query = """
SELECT 
    p.id AS pdf_id,
    p.file_type,
    p.popup_email_content_language,
    CASE 
        WHEN p.file_type = 'ebook' THEN pf.file_name 
        ELSE p.pdf_file 
    END AS file_name,
    CASE
        WHEN p.folder_name IS NOT NULL AND p.folder_name != '0'
        THEN p.folder_name
        ELSE pf.folder_name
    END AS folder_name
FROM pdfs p
LEFT JOIN pdf_files pf 
    ON pf.pdf_id = p.id
WHERE p.id = :pdf_id
LIMIT 1
"""

als_query = """
            SELECT ptt.user_id, ptt.pdf_id
            FROM pdf_time_tracks ptt
            WHERE ptt.user_id = (
                SELECT id
                FROM users
                WHERE email = :email
                ORDER BY id ASC
                LIMIT 1
            )
            ORDER BY ptt.starttime DESC
            LIMIT 1
        """

markov_query = """
        WITH recent_reads AS (
            SELECT 
                ptt.user_id,
                ptt.pdf_id,
                p.popup_email_content_language,
                ptt.starttime
            FROM pdf_time_tracks ptt
            JOIN pdfs p ON p.id = ptt.pdf_id
            WHERE ptt.user_id = (
                SELECT id
                FROM users
                WHERE email = :email
                ORDER BY id ASC
                LIMIT 1
            )
            ORDER BY ptt.starttime DESC
            LIMIT 5
        ),

        majority_language AS (
            SELECT popup_email_content_language
            FROM recent_reads
            GROUP BY popup_email_content_language
            ORDER BY COUNT(*) DESC
            LIMIT 1
        )

        SELECT rr.user_id, rr.pdf_id
        FROM recent_reads rr
        JOIN majority_language ml 
        ON rr.popup_email_content_language = ml.popup_email_content_language
        ORDER BY rr.starttime DESC
        LIMIT 1;
        """

qdrant_query = """
        WITH recent_reads AS (
            SELECT 
                ptt.user_id,
                ptt.pdf_id,
                p.popup_email_content_language,
                ptt.starttime
            FROM pdf_time_tracks ptt
            JOIN pdfs p ON p.id = ptt.pdf_id
            WHERE ptt.user_id = (
                SELECT id
                FROM users
                WHERE email = :email
                ORDER BY id ASC
                LIMIT 1
            )
            ORDER BY ptt.starttime DESC
            LIMIT 5
        ),

        majority_language AS (
            SELECT popup_email_content_language
            FROM recent_reads
            GROUP BY popup_email_content_language
            ORDER BY COUNT(*) DESC
            LIMIT 1
        )

        SELECT rr.user_id, rr.pdf_id
        FROM recent_reads rr
        JOIN majority_language ml 
        ON rr.popup_email_content_language = ml.popup_email_content_language
        ORDER BY rr.starttime DESC
        LIMIT 1;
        """