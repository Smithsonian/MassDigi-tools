<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:ead2002="urn:isbn:1-931666-22-9"
    exclude-result-prefixes="xs"
    version="3.0">
    <xsl:mode on-no-match="shallow-copy"/> 
    <xsl:output method="xml" encoding="UTF-8" indent="1"/>
    
    <!-- rather than assume that enumerated components will always be serialized, we use this shorthand regex expression to match any c, c01 - c12, elements -->
    <xsl:param name="c" select="'^c$|^c[0|1]'" as="xs:string"/>
    
    <xsl:template match="*:dsc">
        <xsl:variable name="eadid" select="ancestor::*:archdesc/*:did/*:unitid[1]"/>
        <!-- Our expectations are that:
                1)  we only need to processes the 3 lowest-levels of description, hereby referred to as grandparent, parent, and children levels (where parantage is calculated from the terminal component level, i.e. the 'children' levels).
                2)  those children levels must have container elements (ideally the other levels will NOT have containers, but we will add that check to another validation layer)
            This XPath statement selects all grandparent elements, then, regardless of their depth in the hiearchy, then kicks off the process with the use of modes
            -->
        <xsl:variable name="grandparents" select=".//*[matches(local-name(), $c)][*[matches(local-name(), $c)]/*[matches(local-name(), $c)]/*:did/*:container]" as="node()*"/>
        <xsl:variable name="terminal-components-with-no-containers" select=".//*[matches(local-name(), $c)][not(*:did/*:container)][not(*[matches(local-name(), $c)])]" as="node()*"/>
        <xsl:variable name="problem-component-count" select="count($terminal-components-with-no-containers)"/>
        <xsl:if test="$terminal-components-with-no-containers">
            <xsl:message terminate="no" expand-text="1">
                {$problem-component-count} terminal component{if ($problem-component-count gt 1) then 's' else ''} without containers {if ($problem-component-count gt 1) then 'have' else 'has'} been found in {$eadid}. Though valid, this violates the expected data model for the JPCA project.
            </xsl:message>
        </xsl:if>
        <xsl:copy>
            <xsl:apply-templates select="$grandparents" mode="grandparent"/>
        </xsl:copy>
    </xsl:template>
    
    <!--   grandparents   -> c01   -->
    <xsl:template match="*[matches(local-name(), $c)]" mode="grandparent">
        <xsl:element name="c01" namespace="urn:isbn:1-931666-22-9">
            <xsl:apply-templates select="@*|*[not(matches(local-name(), $c))]"/>
            <xsl:apply-templates select="*[matches(local-name(), $c)]" mode="parent"/>
        </xsl:element>
    </xsl:template>
    
    <!--   parents        -> c02   -->
    <xsl:template match="*[matches(local-name(), $c)]" mode="parent">
        <xsl:element name="c02" namespace="urn:isbn:1-931666-22-9">
            <xsl:apply-templates select="@*|*[not(matches(local-name(), $c))]"/>
            <xsl:apply-templates select="*[matches(local-name(), $c)]" mode="children"/>
        </xsl:element>
    </xsl:template>
    
    <!--   children       -> c03   -->
    <xsl:template match="*[matches(local-name(), $c)]" mode="children">
        <!-- keeping this test as is for now, as it would signal other problems that should not be ignored at this stage -->
        <xsl:if test="*[matches(local-name(), $c)]">
            <xsl:message terminate="yes" select="'Though valid, it is not expected that our children components should have any further levels of description, so the transformation has ceased!'"/>
        </xsl:if>
        <xsl:element name="c03" namespace="urn:isbn:1-931666-22-9">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:element>
    </xsl:template>
    
</xsl:stylesheet>