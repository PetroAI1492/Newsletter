<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <html>
      <head>
        <title>Energy Empire Newsletter</title>
        <link rel="stylesheet" type="text/css" href="style.css"/>
      </head>
      <body>
        <h1><xsl:value-of select="newsletter/subject"/></h1>
        <table>
          <tr>
            <th>Region</th>
            <th>Production (bbl)</th>
          </tr>
          <xsl:for-each select="newsletter/oil_data/region">
            <tr>
              <td><xsl:value-of select="@name"/></td>
              <td><xsl:value-of select="production"/></td>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
