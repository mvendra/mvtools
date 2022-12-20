#!/usr/bin/env python3

import sys
import os

import path_utils
import prjboot_util

import standard_c
import standard_cpp

def msvc17_prj_hex_id():
    prj_id = prjboot_util.random_32_hex_string_dashed()
    return prj_id

def msvc17_prjfile_hex_id():
    prjfile_id = prjboot_util.random_32_hex_string_dashed()
    return prjfile_id

def msvc17_solution_hex_id():
    sln_id = prjboot_util.random_32_hex_string_dashed()
    return sln_id

def msvc17slnfile_contents(project_name, project_hex_id, project_projfile_hex_id, solution_hex_id):

    r = ""
    r += "\nMicrosoft Visual Studio Solution File, Format Version 12.00\n"
    r += "# Visual Studio Version 17\n"
    r += "VisualStudioVersion = 17.1.32210.238\n"
    r += "MinimumVisualStudioVersion = 10.0.40219.1\n"
    r += "Project(\"{%s}\") = \"%s\", \"%s.vcxproj\", \"{%s}\"\n" % (project_hex_id, project_name, project_name, project_projfile_hex_id)
    r += "EndProject\n"
    r += "Global\n"
    r += "\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\n"
    r += "\t\tDebug|x64 = Debug|x64\n"
    r += "\t\tRelease|x64 = Release|x64\n"
    r += "\tEndGlobalSection\n"
    r += "\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\n"
    r += "\t\t{%s}.Debug|x64.ActiveCfg = Debug|x64\n" % project_projfile_hex_id
    r += "\t\t{%s}.Debug|x64.Build.0 = Debug|x64\n" % project_projfile_hex_id
    r += "\t\t{%s}.Release|x64.ActiveCfg = Release|x64\n" % project_projfile_hex_id
    r += "\t\t{%s}.Release|x64.Build.0 = Release|x64\n" % project_projfile_hex_id
    r += "\tEndGlobalSection\n"
    r += "\tGlobalSection(SolutionProperties) = preSolution\n"
    r += "\t\tHideSolutionNode = FALSE\n"
    r += "\tEndGlobalSection\n"
    r += "\tGlobalSection(ExtensibilityGlobals) = postSolution\n"
    r += "\t\tSolutionGuid = {%s}\n" % solution_hex_id
    r += "\tEndGlobalSection\n"
    r += "EndGlobal\n"

    ba_r = bytearray(b"\xEF\xBB\xBF")
    ba_r.extend(map(ord, r))
    return ba_r

def msvc17projfile_contents_c(project_name, project_hex_id):

    r = ""
    r += "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    r += "<Project DefaultTargets=\"Build\" xmlns=\"http://schemas.microsoft.com/developer/msbuild/2003\">\n"
    r += "  <ItemGroup Label=\"ProjectConfigurations\">\n"
    r += "    <ProjectConfiguration Include=\"Debug|x64\">\n"
    r += "      <Configuration>Debug</Configuration>\n"
    r += "      <Platform>x64</Platform>\n"
    r += "    </ProjectConfiguration>\n"
    r += "    <ProjectConfiguration Include=\"Release|x64\">\n"
    r += "      <Configuration>Release</Configuration>\n"
    r += "      <Platform>x64</Platform>\n"
    r += "    </ProjectConfiguration>\n"
    r += "  </ItemGroup>\n"
    r += "  <ItemGroup>\n"
    r += "    <ClCompile Include=\"..\\..\\src\\main.c\" />\n"
    r += "    <ClCompile Include=\"..\\..\\src\\subfolder\\second.c\" />\n"
    r += "  </ItemGroup>\n"
    r += "  <PropertyGroup Label=\"Globals\">\n"
    r += "    <VCProjectVersion>16.0</VCProjectVersion>\n"
    r += "    <Keyword>Win32Proj</Keyword>\n"
    r += "    <ProjectGuid>{%s}</ProjectGuid>\n" % project_hex_id.lower()
    r += "    <RootNamespace>%s</RootNamespace>\n" % project_name
    r += "    <WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>\n"
    r += "  </PropertyGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.Default.props\" />\n"
    r += "  <PropertyGroup Condition=\"'$(Configuration)|$(Platform)'=='Debug|x64'\" Label=\"Configuration\">\n"
    r += "    <ConfigurationType>Application</ConfigurationType>\n"
    r += "    <UseDebugLibraries>true</UseDebugLibraries>\n"
    r += "    <PlatformToolset>v143</PlatformToolset>\n"
    r += "    <CharacterSet>Unicode</CharacterSet>\n"
    r += "  </PropertyGroup>\n"
    r += "  <PropertyGroup Condition=\"'$(Configuration)|$(Platform)'=='Release|x64'\" Label=\"Configuration\">\n"
    r += "    <ConfigurationType>Application</ConfigurationType>\n"
    r += "    <UseDebugLibraries>false</UseDebugLibraries>\n"
    r += "    <PlatformToolset>v143</PlatformToolset>\n"
    r += "    <WholeProgramOptimization>true</WholeProgramOptimization>\n"
    r += "    <CharacterSet>Unicode</CharacterSet>\n"
    r += "  </PropertyGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.props\" />\n"
    r += "  <ImportGroup Label=\"ExtensionSettings\">\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"Shared\">\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"PropertySheets\" Condition=\"'$(Configuration)|$(Platform)'=='Debug|x64'\">\n"
    r += "    <Import Project=\"$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props\" Condition=\"exists('$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props')\" Label=\"LocalAppDataPlatform\" />\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"PropertySheets\" Condition=\"'$(Configuration)|$(Platform)'=='Release|x64'\">\n"
    r += "    <Import Project=\"$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props\" Condition=\"exists('$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props')\" Label=\"LocalAppDataPlatform\" />\n"
    r += "  </ImportGroup>\n"
    r += "  <PropertyGroup Label=\"UserMacros\" />\n"
    r += "  <PropertyGroup Condition=\"'$(Configuration)|$(Platform)'=='Debug|x64'\">\n"
    r += "    <LinkIncremental>true</LinkIncremental>\n"
    r += "    <OutDir>$(SolutionDir)..\\..\\run\\windows_$(PlatformTarget)_$(Configuration)\\</OutDir>\n"
    r += "    <IntDir>$(SolutionDir)..\\..\\build\\windows_$(PlatformTarget)_$(Configuration)\\</IntDir>\n"
    r += "  </PropertyGroup>\n"
    r += "  <PropertyGroup Condition=\"'$(Configuration)|$(Platform)'=='Release|x64'\">\n"
    r += "    <LinkIncremental>false</LinkIncremental>\n"
    r += "    <OutDir>$(SolutionDir)..\\..\\run\\windows_$(PlatformTarget)_$(Configuration)\\</OutDir>\n"
    r += "    <IntDir>$(SolutionDir)..\\..\\build\\windows_$(PlatformTarget)_$(Configuration)\\</IntDir>\n"
    r += "  </PropertyGroup>\n"
    r += "  <ItemDefinitionGroup Condition=\"'$(Configuration)|$(Platform)'=='Debug|x64'\">\n"
    r += "    <ClCompile>\n"
    r += "%s\n" % (prjboot_util.format_xml_tag_openclose("      ", "AdditionalOptions", prjboot_util.unroll_options_with_suffix(" ", "%(AdditionalOptions)", standard_c.c_compiler_flags_debug_msvc() + standard_c.c_compiler_flags_windows_msvc())))
    r += "      <WarningLevel>Level3</WarningLevel>\n"
    r += "      <SDLCheck>true</SDLCheck>\n"
    r += "      <PreprocessorDefinitions>_DEBUG;_CONSOLE;_CRT_SECURE_NO_WARNINGS;%(PreprocessorDefinitions)</PreprocessorDefinitions>\n"
    r += "      <ConformanceMode>true</ConformanceMode>\n"
    r += "      <AdditionalIncludeDirectories>%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>\n"
    r += "      <LanguageStandard_C>%s</LanguageStandard_C>\n" % standard_c.c_compiler_standard_windows_msvc()
    r += "    </ClCompile>\n"
    r += "    <Link>\n"
    r += "      <SubSystem>Console</SubSystem>\n"
    r += "      <GenerateDebugInformation>true</GenerateDebugInformation>\n"
    r += "      <AdditionalLibraryDirectories>%(AdditionalLibraryDirectories)</AdditionalLibraryDirectories>\n"
    r += "      <AdditionalDependencies>%(AdditionalDependencies)</AdditionalDependencies>\n"
    r += "    </Link>\n"
    r += "  </ItemDefinitionGroup>\n"
    r += "  <ItemDefinitionGroup Condition=\"'$(Configuration)|$(Platform)'=='Release|x64'\">\n"
    r += "    <ClCompile>\n"
    r += "%s\n" % (prjboot_util.format_xml_tag_openclose("      ", "AdditionalOptions", prjboot_util.unroll_options_with_suffix(" ", "%(AdditionalOptions)", standard_c.c_compiler_flags_release_msvc() + standard_c.c_compiler_flags_windows_msvc())))
    r += "      <WarningLevel>Level3</WarningLevel>\n"
    r += "      <FunctionLevelLinking>true</FunctionLevelLinking>\n"
    r += "      <IntrinsicFunctions>true</IntrinsicFunctions>\n"
    r += "      <SDLCheck>true</SDLCheck>\n"
    r += "      <PreprocessorDefinitions>NDEBUG;_CONSOLE;_CRT_SECURE_NO_WARNINGS;%(PreprocessorDefinitions)</PreprocessorDefinitions>\n"
    r += "      <ConformanceMode>true</ConformanceMode>\n"
    r += "      <AdditionalIncludeDirectories>%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>\n"
    r += "      <LanguageStandard_C>%s</LanguageStandard_C>\n" % standard_c.c_compiler_standard_windows_msvc()
    r += "    </ClCompile>\n"
    r += "    <Link>\n"
    r += "      <SubSystem>Console</SubSystem>\n"
    r += "      <EnableCOMDATFolding>true</EnableCOMDATFolding>\n"
    r += "      <OptimizeReferences>true</OptimizeReferences>\n"
    r += "      <GenerateDebugInformation>true</GenerateDebugInformation>\n"
    r += "      <AdditionalLibraryDirectories>%(AdditionalLibraryDirectories)</AdditionalLibraryDirectories>\n"
    r += "      <AdditionalDependencies>%(AdditionalDependencies)</AdditionalDependencies>\n"
    r += "    </Link>\n"
    r += "  </ItemDefinitionGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />\n"
    r += "  <ImportGroup Label=\"ExtensionTargets\">\n"
    r += "  </ImportGroup>\n"
    r += "</Project>\n"

    ba_r = bytearray()
    ba_r.extend(map(ord, r))
    return ba_r

def msvc17projfile_filters_contents_c(src_filter_hex_id, src_subfolder_filter_hex_id):

    r = ""
    r += "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    r += "<Project ToolsVersion=\"4.0\" xmlns=\"http://schemas.microsoft.com/developer/msbuild/2003\">\n"
    r += "  <ItemGroup>\n"
    r += "    <ClCompile Include=\"..\\..\\src\\main.c\">\n"
    r += "      <Filter>src</Filter>\n"
    r += "    </ClCompile>\n"
    r += "    <ClCompile Include=\"..\\..\\src\\subfolder\\second.c\">\n"
    r += "      <Filter>src\\subfolder</Filter>\n"
    r += "    </ClCompile>\n"
    r += "  </ItemGroup>\n"
    r += "  <ItemGroup>\n"
    r += "    <Filter Include=\"src\">\n"
    r += "      <UniqueIdentifier>{%s}</UniqueIdentifier>\n" % src_filter_hex_id.lower()
    r += "    </Filter>\n"
    r += "    <Filter Include=\"src\\subfolder\">\n"
    r += "      <UniqueIdentifier>{%s}</UniqueIdentifier>\n" % src_subfolder_filter_hex_id.lower()
    r += "    </Filter>\n"
    r += "  </ItemGroup>\n"
    r += "</Project>"

    ba_r = bytearray(b"\xEF\xBB\xBF")
    ba_r.extend(map(ord, r))
    return ba_r

def generate_msvc17_c(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_prj = path_utils.concat_path(prj_fullname_base, "proj")
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # generate the actual Visual Studio project and solution files
    project_hex_id = msvc17_prj_hex_id()
    project_projfile_hex_id = msvc17_prjfile_hex_id()
    solution_hex_id = msvc17_solution_hex_id()
    src_filter_hex_id = msvc17_solution_hex_id()
    src_subfolder_filter_hex_id = msvc17_solution_hex_id()
    base_prj_msvc17 = path_utils.concat_path(base_prj, "msvc17_c")
    os.mkdir(base_prj_msvc17)
    base_prj_filters_msvc17_fn = path_utils.concat_path(base_prj_msvc17, "%s.vcxproj.filters" % project_name)
    base_prj_msvc17_fn = path_utils.concat_path(base_prj_msvc17, "%s.vcxproj" % project_name)
    base_prj_msvc17_sln = path_utils.concat_path(base_prj_msvc17, "%s.sln" % project_name)
    prjboot_util.writecontents(base_prj_filters_msvc17_fn, msvc17projfile_filters_contents_c(src_filter_hex_id, src_subfolder_filter_hex_id))
    prjboot_util.writecontents(base_prj_msvc17_fn, msvc17projfile_contents_c(project_name, project_projfile_hex_id))
    prjboot_util.writecontents(base_prj_msvc17_sln, msvc17slnfile_contents(project_name, project_hex_id, project_projfile_hex_id, solution_hex_id))

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc17_c/.vs")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc17_c/%s.VC.db" % project_name)
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc17_c/%s.VC.VC.opendb" % project_name)
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc17_c/%s.vcxproj.user" % project_name)

    # main C file
    base_src_main_c_fn = path_utils.concat_path(base_src, "main.c")
    if not prjboot_util.writecontents(base_src_main_c_fn, standard_c.get_main_c_app()):
        return False, "Failed creating [%s]" % base_src_main_c_fn

    # secondary C file
    base_src_subfolder = path_utils.concat_path(base_src, "subfolder")
    prjboot_util.makedir_if_needed(base_src_subfolder)
    base_src_subfolder_secondary_c_fn = path_utils.concat_path(base_src_subfolder, "second.c")
    if not prjboot_util.writecontents(base_src_subfolder_secondary_c_fn, prjboot_util.secondary_c_app()):
        return False, "Failed creating [%s]" % base_src_subfolder_secondary_c_fn

    return True, None

def msvc15_solution_hex_id():
    sln_id = prjboot_util.random_32_hex_string_dashed()
    return sln_id

def msvc15_prj_hex_id():
    prj_id = prjboot_util.random_32_hex_string_dashed()
    return prj_id

def msvc15slnfile_contents(solution_hex_id, project_name, project_hex_id):

    r = ""
    r += "\nMicrosoft Visual Studio Solution File, Format Version 12.00\n"
    r += "# Visual Studio 15\n"
    r += "VisualStudioVersion = 15.0.26228.9\n"
    r += "MinimumVisualStudioVersion = 10.0.40219.1\n"
    r += "Project(\"{%s}\") = \"%s\", \"%s.vcxproj\", \"{%s}\"\n" % (solution_hex_id, project_name, project_name, project_hex_id)
    r += "EndProject\n"
    r += "Global\n"
    r += "\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\n"
    r += "\t\tDebug|x64 = Debug|x64\n"
    r += "\t\tRelease|x64 = Release|x64\n"
    r += "\tEndGlobalSection\n"
    r += "\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\n"
    r += "\t\t{%s}.Debug|x64.ActiveCfg = Debug|x64\n" % project_hex_id
    r += "\t\t{%s}.Debug|x64.Build.0 = Debug|x64\n" % project_hex_id
    r += "\t\t{%s}.Release|x64.ActiveCfg = Release|x64\n" % project_hex_id
    r += "\t\t{%s}.Release|x64.Build.0 = Release|x64\n" % project_hex_id
    r += "\tEndGlobalSection\n"
    r += "\tGlobalSection(SolutionProperties) = preSolution\n"
    r += "\t\tHideSolutionNode = FALSE\n"
    r += "\tEndGlobalSection\n"
    r += "EndGlobal\n"

    ba_r = bytearray(b"\xEF\xBB\xBF")
    ba_r.extend(map(ord, r))
    return ba_r

def msvc15projfile_contents_c(project_name, project_hex_id):

    r = ""
    r += "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    r += "<Project DefaultTargets=\"Build\" ToolsVersion=\"15.0\" xmlns=\"http://schemas.microsoft.com/developer/msbuild/2003\">\n"
    r += "  <ItemGroup Label=\"ProjectConfigurations\">\n"
    r += "    <ProjectConfiguration Include=\"Debug|x64\">\n"
    r += "      <Configuration>Debug</Configuration>\n"
    r += "      <Platform>x64</Platform>\n"
    r += "    </ProjectConfiguration>\n"
    r += "    <ProjectConfiguration Include=\"Release|x64\">\n"
    r += "      <Configuration>Release</Configuration>\n"
    r += "      <Platform>x64</Platform>\n"
    r += "    </ProjectConfiguration>\n"
    r += "  </ItemGroup>\n"
    r += "  <PropertyGroup Label=\"Globals\">\n"
    r += "    <VCProjectVersion>15.0</VCProjectVersion>\n"
    r += "    <ProjectGuid>{%s}</ProjectGuid>\n" % project_hex_id
    r += "    <RootNamespace>%s</RootNamespace>\n" % project_name
    r += "    <WindowsTargetPlatformVersion>10.0.14393.0</WindowsTargetPlatformVersion>\n"
    r += "  </PropertyGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\Microsoft.Cpp.Default.props\" />\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\" Label=\"Configuration\">\n"
    r += "    <ConfigurationType>Application</ConfigurationType>\n"
    r += "    <UseDebugLibraries>true</UseDebugLibraries>\n"
    r += "    <PlatformToolset>v141</PlatformToolset>\n"
    r += "    <CharacterSet>MultiByte</CharacterSet>\n"
    r += "  </PropertyGroup>\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\" Label=\"Configuration\">\n"
    r += "    <ConfigurationType>Application</ConfigurationType>\n"
    r += "    <UseDebugLibraries>false</UseDebugLibraries>\n"
    r += "    <PlatformToolset>v141</PlatformToolset>\n"
    r += "    <WholeProgramOptimization>true</WholeProgramOptimization>\n"
    r += "    <CharacterSet>MultiByte</CharacterSet>\n"
    r += "  </PropertyGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\Microsoft.Cpp.props\" />\n"
    r += "  <ImportGroup Label=\"ExtensionSettings\">\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"Shared\">\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"PropertySheets\" Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\">\n"
    r += "    <Import Project=\"$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\" Condition=\"exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')\" Label=\"LocalAppDataPlatform\" />\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"PropertySheets\" Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\">\n"
    r += "    <Import Project=\"$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\" Condition=\"exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')\" Label=\"LocalAppDataPlatform\" />\n"
    r += "  </ImportGroup>\n"
    r += "  <PropertyGroup Label=\"UserMacros\" />\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\">\n"
    r += "    <OutDir>$(SolutionDir)..\\..\\run\windows_$(PlatformTarget)_$(Configuration)\\</OutDir>\n"
    r += "    <IntDir>$(SolutionDir)..\\..\\build\windows_$(PlatformTarget)_$(Configuration)\\</IntDir>\n"
    r += "  </PropertyGroup>\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\">\n"
    r += "    <OutDir>$(SolutionDir)..\\..\\run\\windows_$(PlatformTarget)_$(Configuration)\\</OutDir>\n"
    r += "    <IntDir>$(SolutionDir)..\\..\\build\\windows_$(PlatformTarget)_$(Configuration)\\</IntDir>\n"
    r += "  </PropertyGroup>\n"
    r += "  <ItemDefinitionGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\">\n"
    r += "    <ClCompile>\n"
    r += "%s\n" % (prjboot_util.format_xml_tag_openclose("      ", "AdditionalOptions", prjboot_util.unroll_options_with_suffix(" ", "%(AdditionalOptions)", standard_c.c_compiler_flags_debug_msvc() + standard_c.c_compiler_flags_windows_msvc())))
    r += "      <WarningLevel>Level3</WarningLevel>\n"
    r += "      <Optimization>Disabled</Optimization>\n"
    r += "      <SDLCheck>true</SDLCheck>\n"
    r += "    </ClCompile>\n"
    r += "  </ItemDefinitionGroup>\n"
    r += "  <ItemDefinitionGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\">\n"
    r += "    <ClCompile>\n"
    r += "%s\n" % (prjboot_util.format_xml_tag_openclose("      ", "AdditionalOptions", prjboot_util.unroll_options_with_suffix(" ", "%(AdditionalOptions)", standard_c.c_compiler_flags_release_msvc() + standard_c.c_compiler_flags_windows_msvc())))
    r += "      <WarningLevel>Level3</WarningLevel>\n"
    r += "      <Optimization>MaxSpeed</Optimization>\n"
    r += "      <FunctionLevelLinking>true</FunctionLevelLinking>\n"
    r += "      <IntrinsicFunctions>true</IntrinsicFunctions>\n"
    r += "      <SDLCheck>true</SDLCheck>\n"
    r += "    </ClCompile>\n"
    r += "    <Link>\n"
    r += "      <EnableCOMDATFolding>true</EnableCOMDATFolding>\n"
    r += "      <OptimizeReferences>true</OptimizeReferences>\n"
    r += "    </Link>\n"
    r += "  </ItemDefinitionGroup>\n"
    r += "  <ItemGroup>\n"
    r += "    <ClCompile Include=\"..\\..\\src\\main.c\" />\n"
    r += "    <ClCompile Include=\"..\\..\\src\\subfolder\\second.c\" />\n"
    r += "  </ItemGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />\n"
    r += "  <ImportGroup Label=\"ExtensionTargets\">\n"
    r += "  </ImportGroup>\n"
    r += "</Project>\n"

    ba_r = bytearray(b"\xEF\xBB\xBF")
    ba_r.extend(map(ord, r))
    return ba_r

def msvc15projfile_contents_cpp(project_name, project_hex_id):

    r = ""
    r += "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    r += "<Project DefaultTargets=\"Build\" ToolsVersion=\"15.0\" xmlns=\"http://schemas.microsoft.com/developer/msbuild/2003\">\n"
    r += "  <ItemGroup Label=\"ProjectConfigurations\">\n"
    r += "    <ProjectConfiguration Include=\"Debug|x64\">\n"
    r += "      <Configuration>Debug</Configuration>\n"
    r += "      <Platform>x64</Platform>\n"
    r += "    </ProjectConfiguration>\n"
    r += "    <ProjectConfiguration Include=\"Release|x64\">\n"
    r += "      <Configuration>Release</Configuration>\n"
    r += "      <Platform>x64</Platform>\n"
    r += "    </ProjectConfiguration>\n"
    r += "  </ItemGroup>\n"
    r += "  <PropertyGroup Label=\"Globals\">\n"
    r += "    <VCProjectVersion>15.0</VCProjectVersion>\n"
    r += "    <ProjectGuid>{%s}</ProjectGuid>\n" % project_hex_id
    r += "    <RootNamespace>%s</RootNamespace>\n" % project_name
    r += "    <WindowsTargetPlatformVersion>10.0.14393.0</WindowsTargetPlatformVersion>\n"
    r += "  </PropertyGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\Microsoft.Cpp.Default.props\" />\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\" Label=\"Configuration\">\n"
    r += "    <ConfigurationType>Application</ConfigurationType>\n"
    r += "    <UseDebugLibraries>true</UseDebugLibraries>\n"
    r += "    <PlatformToolset>v141</PlatformToolset>\n"
    r += "    <CharacterSet>MultiByte</CharacterSet>\n"
    r += "  </PropertyGroup>\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\" Label=\"Configuration\">\n"
    r += "    <ConfigurationType>Application</ConfigurationType>\n"
    r += "    <UseDebugLibraries>false</UseDebugLibraries>\n"
    r += "    <PlatformToolset>v141</PlatformToolset>\n"
    r += "    <WholeProgramOptimization>true</WholeProgramOptimization>\n"
    r += "    <CharacterSet>MultiByte</CharacterSet>\n"
    r += "  </PropertyGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\Microsoft.Cpp.props\" />\n"
    r += "  <ImportGroup Label=\"ExtensionSettings\">\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"Shared\">\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"PropertySheets\" Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\">\n"
    r += "    <Import Project=\"$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\" Condition=\"exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')\" Label=\"LocalAppDataPlatform\" />\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"PropertySheets\" Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\">\n"
    r += "    <Import Project=\"$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\" Condition=\"exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')\" Label=\"LocalAppDataPlatform\" />\n"
    r += "  </ImportGroup>\n"
    r += "  <PropertyGroup Label=\"UserMacros\" />\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\">\n"
    r += "    <OutDir>$(SolutionDir)..\\..\\run\windows_$(PlatformTarget)_$(Configuration)\\</OutDir>\n"
    r += "    <IntDir>$(SolutionDir)..\\..\\build\windows_$(PlatformTarget)_$(Configuration)\\</IntDir>\n"
    r += "  </PropertyGroup>\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\">\n"
    r += "    <OutDir>$(SolutionDir)..\\..\\run\\windows_$(PlatformTarget)_$(Configuration)\\</OutDir>\n"
    r += "    <IntDir>$(SolutionDir)..\\..\\build\\windows_$(PlatformTarget)_$(Configuration)\\</IntDir>\n"
    r += "  </PropertyGroup>\n"
    r += "  <ItemDefinitionGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\">\n"
    r += "    <ClCompile>\n"
    r += "%s\n" % (prjboot_util.format_xml_tag_openclose("      ", "AdditionalOptions", prjboot_util.unroll_options_with_suffix(" ", "%(AdditionalOptions)", standard_cpp.cpp_compiler_flags_debug_msvc() + standard_cpp.cpp_compiler_flags_windows_msvc())))
    r += "      <WarningLevel>Level3</WarningLevel>\n"
    r += "      <Optimization>Disabled</Optimization>\n"
    r += "      <SDLCheck>true</SDLCheck>\n"
    r += "    </ClCompile>\n"
    r += "  </ItemDefinitionGroup>\n"
    r += "  <ItemDefinitionGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\">\n"
    r += "    <ClCompile>\n"
    r += "%s\n" % (prjboot_util.format_xml_tag_openclose("      ", "AdditionalOptions", prjboot_util.unroll_options_with_suffix(" ", "%(AdditionalOptions)", standard_cpp.cpp_compiler_flags_release_msvc() + standard_cpp.cpp_compiler_flags_windows_msvc())))
    r += "      <WarningLevel>Level3</WarningLevel>\n"
    r += "      <Optimization>MaxSpeed</Optimization>\n"
    r += "      <FunctionLevelLinking>true</FunctionLevelLinking>\n"
    r += "      <IntrinsicFunctions>true</IntrinsicFunctions>\n"
    r += "      <SDLCheck>true</SDLCheck>\n"
    r += "    </ClCompile>\n"
    r += "    <Link>\n"
    r += "      <EnableCOMDATFolding>true</EnableCOMDATFolding>\n"
    r += "      <OptimizeReferences>true</OptimizeReferences>\n"
    r += "    </Link>\n"
    r += "  </ItemDefinitionGroup>\n"
    r += "  <ItemGroup>\n"
    r += "    <ClCompile Include=\"..\\..\\src\\main.cpp\" />\n"
    r += "    <ClCompile Include=\"..\\..\\src\\subfolder\\second.cpp\" />\n"
    r += "  </ItemGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />\n"
    r += "  <ImportGroup Label=\"ExtensionTargets\">\n"
    r += "  </ImportGroup>\n"
    r += "</Project>\n"

    ba_r = bytearray(b"\xEF\xBB\xBF")
    ba_r.extend(map(ord, r))
    return ba_r

def generate_msvc15_c(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_prj = path_utils.concat_path(prj_fullname_base, "proj")
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # generate the actual Visual Studio project and solution files
    project_hex_id = msvc15_prj_hex_id()
    solution_hex_id = msvc15_solution_hex_id()
    base_prj_msvc15 = path_utils.concat_path(base_prj, "msvc15_c")
    os.mkdir(base_prj_msvc15)
    base_prj_msvc15_fn = path_utils.concat_path(base_prj_msvc15, "%s.vcxproj" % project_name)
    base_prj_msvc15_sln = path_utils.concat_path(base_prj_msvc15, "%s.sln" % project_name)
    prjboot_util.writecontents(base_prj_msvc15_fn, msvc15projfile_contents_c(project_name, project_hex_id))
    prjboot_util.writecontents(base_prj_msvc15_sln, msvc15slnfile_contents(solution_hex_id, project_name, project_hex_id))

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_c/.vs")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_c/%s.VC.db" % project_name)
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_c/%s.VC.VC.opendb" % project_name)
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_c/%s.vcxproj.user" % project_name)

    # main C file
    base_src_main_c_fn = path_utils.concat_path(base_src, "main.c")
    if not prjboot_util.writecontents(base_src_main_c_fn, standard_c.get_main_c_app()):
        return False, "Failed creating [%s]" % base_src_main_c_fn

    # secondary C file
    base_src_subfolder = path_utils.concat_path(base_src, "subfolder")
    prjboot_util.makedir_if_needed(base_src_subfolder)
    base_src_subfolder_secondary_c_fn = path_utils.concat_path(base_src_subfolder, "second.c")
    if not prjboot_util.writecontents(base_src_subfolder_secondary_c_fn, prjboot_util.secondary_c_app()):
        return False, "Failed creating [%s]" % base_src_subfolder_secondary_c_fn

    return True, None

def generate_msvc15_cpp(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_prj = path_utils.concat_path(prj_fullname_base, "proj")
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # generate the actual Visual Studio project and solution files
    project_hex_id = msvc15_prj_hex_id()
    solution_hex_id = msvc15_solution_hex_id()
    base_prj_msvc15 = path_utils.concat_path(base_prj, "msvc15_cpp")
    os.mkdir(base_prj_msvc15)
    base_prj_msvc15_fn = path_utils.concat_path(base_prj_msvc15, "%s.vcxproj" % project_name)
    base_prj_msvc15_sln = path_utils.concat_path(base_prj_msvc15, "%s.sln" % project_name)
    prjboot_util.writecontents(base_prj_msvc15_fn, msvc15projfile_contents_cpp(project_name, project_hex_id))
    prjboot_util.writecontents(base_prj_msvc15_sln, msvc15slnfile_contents(solution_hex_id, project_name, project_hex_id))

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_cpp/.vs")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_cpp/%s.VC.db" % project_name)
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_cpp/%s.VC.VC.opendb" % project_name)
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_cpp/%s.vcxproj.user" % project_name)

    # main C++ file
    base_src_main_cpp_fn = path_utils.concat_path(base_src, "main.cpp")
    if not prjboot_util.writecontents(base_src_main_cpp_fn, standard_cpp.get_main_cpp_app()):
        return False, "Failed creating [%s]" % base_src_main_cpp_fn

    # secondary C++ file
    base_src_subfolder = path_utils.concat_path(base_src, "subfolder")
    prjboot_util.makedir_if_needed(base_src_subfolder)
    base_src_subfolder_secondary_cpp_fn = path_utils.concat_path(base_src_subfolder, "second.cpp")
    if not prjboot_util.writecontents(base_src_subfolder_secondary_cpp_fn, prjboot_util.secondary_c_app()):
        return False, "Failed creating [%s]" % base_src_subfolder_secondary_cpp_fn

    return True, None
