#!/usr/bin/env python

import sys
import os

def writecontents(filename, contents):
    with open(filename, "w") as f:
        f.write(contents)

def prjboot_validate(target_dir, project_name):

    if os.path.exists(os.path.join(target_dir, project_name)):
        print("%s already exists. Specify another project name." % os.path.join(target_dir, project_name))
        return False

    if not os.path.exists(target_dir):
        print("%s does not exist. Specify another target directory." % target_dir)
        return False

    return True

def main_contents():
    r = "#include <iostream>\n\n"
    r += "int main(int argc, char *argv[]){\n";
    r += "    (void)argc; (void)argv;\n"
    r += "    std::cout << \"echo\" << std::endl;\n"
    r += "    return 0;\n"
    r += "}\n"
    return r

def codelite_projfile_contents(project_name):
    r = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    r += "<CodeLite_Project Name=\"%s\" InternalType=\"Console\">\n" % project_name
    r += "  <Plugins>\n"
    r += "    <Plugin Name=\"qmake\">\n"
    r += "      <![CDATA[00020001N0005Debug0000000000000001N0007Release000000000000]]>\n"
    r += "    </Plugin>\n"
    r += "    <Plugin Name=\"CMakePlugin\">\n"
    r += "      <![CDATA[[{\n"
    r += "  \"name\": \"Debug\",\n"
    r += "  \"enabled\": false,\n"
    r += "  \"buildDirectory\": \"build\",\n"
    r += "  \"sourceDirectory\": \"$(ProjectPath)\",\n"
    r += "  \"generator\": \"\",\n"
    r += "  \"buildType\": \"\",\n"
    r += "  \"arguments\": [],\n"
    r += "  \"parentProject\": \"\"\n"
    r += " }, {\n"
    r += "  \"name\": \"Debug (LLVM)\",\n"
    r += "  \"enabled\": false,\n"
    r += "  \"buildDirectory\": \"build\",\n"
    r += "  \"sourceDirectory\": \"$(ProjectPath)\",\n"
    r += "  \"generator\": \"\",\n"
    r += "  \"buildType\": \"\",\n"
    r += "  \"arguments\": [],\n"
    r += "  \"parentProject\": \"\"\n"
    r += " }, {\n"
    r += "  \"name\": \"Release\",\n"
    r += "  \"enabled\": false,\n"
    r += "  \"buildDirectory\": \"build\",\n"
    r += "  \"sourceDirectory\": \"$(ProjectPath)\",\n"
    r += "  \"generator\": \"\",\n"
    r += "  \"buildType\": \"\",\n"
    r += "  \"arguments\": [],\n"
    r += "  \"parentProject\": \"\"\n"
    r += " }, {\n"
    r += "  \"name\": \"Release (LLVM)\",\n"
    r += "  \"enabled\": false,\n"
    r += "  \"buildDirectory\": \"build\",\n"
    r += "  \"sourceDirectory\": \"$(ProjectPath)\",\n"
    r += "  \"generator\": \"\",\n"
    r += "  \"buildType\": \"\",\n"
    r += "  \"arguments\": [],\n"
    r += "  \"parentProject\": \"\"\n"
    r += " }]]]>\n"
    r += "    </Plugin>\n"
    r += "  </Plugins>\n"
    r += "  <Description/>\n"
    r += "  <Dependencies/>\n"
    r += "  <VirtualDirectory Name=\"src\">\n"
    r += "    <File Name=\"../../src/main.cpp\"/>\n"
    r += "  </VirtualDirectory>\n"
    r += "  <Settings Type=\"Executable\">\n"
    r += "    <GlobalSettings>\n"
    r += "      <Compiler Options=\"\" C_Options=\"\" Assembler=\"\">\n"
    r += "        <IncludePath Value=\".\"/>\n"
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\">\n"
    r += "        <LibraryPath Value=\".\"/>\n"
    r += "      </Linker>\n"
    r += "      <ResourceCompiler Options=\"\"/>\n"
    r += "    </GlobalSettings>\n"

    r += "    <Configuration Name=\"Debug\" CompilerType=\"GCC\" DebuggerType=\"GNU gdb debugger\" Type=\"Executable\" BuildCmpWithGlobalSettings=\"append\" BuildLnkWithGlobalSettings=\"append\" BuildResWithGlobalSettings=\"append\">\n"
    r += "      <Compiler Options=\"-g;-O0;-pedantic;-W;-std=c++14;-Wall;-Wextra;-Weffc++;-Werror;-fPIC\" C_Options=\"-g;-O0;-Wall\" Assembler=\"\" Required=\"yes\" PreCompiledHeader=\"\" PCHInCommandLine=\"no\" PCHFlags=\"\" PCHFlagsPolicy=\"0\">\n"
    r += "        <IncludePath Value=\"../../src\"/>\n"
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\" Required=\"yes\">\n"
    r += "        <Library Value=\"\"/>\n"
    r += "      </Linker>\n"
    r += "      <ResourceCompiler Options=\"\" Required=\"no\"/>\n"
    r += "      <General OutputFile=\"../../run/linux_x64_debug/$(ProjectName)\" IntermediateDirectory=\"../../build/linux_x64_debug\" Command=\"./$(ProjectName)\" CommandArguments=\"\" UseSeparateDebugArgs=\"no\" DebugArguments=\"\" WorkingDirectory=\"../../run/linux_x64_debug/\" PauseExecWhenProcTerminates=\"yes\" IsGUIProgram=\"no\" IsEnabled=\"yes\"/>\n"
    r += "      <Environment EnvVarSetName=\"&lt;Use Defaults&gt;\" DbgSetName=\"&lt;Use Defaults&gt;\">\n"
    r += "        <![CDATA[]]>\n"
    r += "      </Environment>\n"
    r += "      <Debugger IsRemote=\"no\" RemoteHostName=\"\" RemoteHostPort=\"\" DebuggerPath=\"\" IsExtended=\"yes\">\n"
    r += "        <DebuggerSearchPaths/>\n"
    r += "        <PostConnectCommands/>\n"
    r += "        <StartupCommands/>\n"
    r += "      </Debugger>\n"
    r += "      <PreBuild/>\n"
    r += "      <PostBuild/>\n"
    r += "      <CustomBuild Enabled=\"no\">\n"
    r += "        <RebuildCommand/>\n"
    r += "        <CleanCommand/>\n"
    r += "        <BuildCommand/>\n"
    r += "        <PreprocessFileCommand/>\n"
    r += "        <SingleFileCommand/>\n"
    r += "        <MakefileGenerationCommand/>\n"
    r += "        <ThirdPartyToolName>None</ThirdPartyToolName>\n"
    r += "        <WorkingDirectory/>\n"
    r += "      </CustomBuild>\n"
    r += "      <AdditionalRules>\n"
    r += "        <CustomPostBuild/>\n"
    r += "        <CustomPreBuild/>\n"
    r += "      </AdditionalRules>\n"
    r += "      <Completion EnableCpp11=\"no\" EnableCpp14=\"no\">\n"
    r += "        <ClangCmpFlagsC/>\n"
    r += "        <ClangCmpFlags/>\n"
    r += "        <ClangPP/>\n"
    r += "        <SearchPaths/>\n"
    r += "      </Completion>\n"
    r += "    </Configuration>\n"

    r += "    <Configuration Name=\"Debug (LLVM)\" CompilerType=\"clang( tags/RELEASE_500/final )\" DebuggerType=\"LLDB Debugger\" Type=\"Executable\" BuildCmpWithGlobalSettings=\"append\" BuildLnkWithGlobalSettings=\"append\" BuildResWithGlobalSettings=\"append\">\n"
    r += "      <Compiler Options=\"-g;-O0;-pedantic;-W;-std=c++14;-Wall;-Wextra;-Weffc++;-Werror;-fPIC\" C_Options=\"-g;-O0;-Wall\" Assembler=\"\" Required=\"yes\" PreCompiledHeader=\"\" PCHInCommandLine=\"no\" PCHFlags=\"\" PCHFlagsPolicy=\"0\">\n"
    r += "        <IncludePath Value=\"../../src\"/>\n"
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\" Required=\"yes\"/>\n"
    r += "      <ResourceCompiler Options=\"\" Required=\"no\"/>\n"
    r += "      <General OutputFile=\"../../run/linux_x64_debug/$(ProjectName)\" IntermediateDirectory=\"../../build/linux_x64_debug\" Command=\"./$(ProjectName)\" CommandArguments=\"\" UseSeparateDebugArgs=\"no\" DebugArguments=\"\" WorkingDirectory=\"../../run/linux_x64_debug\" PauseExecWhenProcTerminates=\"yes\" IsGUIProgram=\"no\" IsEnabled=\"yes\"/>\n"
    r += "      <BuildSystem Name=\"Default\"/>\n"
    r += "      <Environment EnvVarSetName=\"&lt;Use Defaults&gt;\" DbgSetName=\"&lt;Use Defaults&gt;\">\n"
    r += "        <![CDATA[]]>\n"
    r += "      </Environment>\n"
    r += "      <Debugger IsRemote=\"no\" RemoteHostName=\"\" RemoteHostPort=\"\" DebuggerPath=\"\" IsExtended=\"yes\">\n"
    r += "        <DebuggerSearchPaths/>\n"
    r += "        <PostConnectCommands/>\n"
    r += "        <StartupCommands/>\n"
    r += "      </Debugger>\n"
    r += "      <PreBuild/>\n"
    r += "      <PostBuild/>\n"
    r += "      <CustomBuild Enabled=\"no\">\n"
    r += "        <RebuildCommand/>\n"
    r += "        <CleanCommand/>\n"
    r += "        <BuildCommand/>\n"
    r += "        <PreprocessFileCommand/>\n"
    r += "        <SingleFileCommand/>\n"
    r += "        <MakefileGenerationCommand/>\n"
    r += "        <ThirdPartyToolName>None</ThirdPartyToolName>\n"
    r += "        <WorkingDirectory/>\n"
    r += "      </CustomBuild>\n"
    r += "      <AdditionalRules>\n"
    r += "        <CustomPostBuild/>\n"
    r += "        <CustomPreBuild/>\n"
    r += "      </AdditionalRules>\n"
    r += "      <Completion EnableCpp11=\"no\" EnableCpp14=\"no\">\n"
    r += "        <ClangCmpFlagsC/>\n"
    r += "        <ClangCmpFlags/>\n"
    r += "        <ClangPP/>\n"
    r += "        <SearchPaths/>\n"
    r += "      </Completion>\n"
    r += "    </Configuration>\n"

    r += "    <Configuration Name=\"Release\" CompilerType=\"GCC\" DebuggerType=\"GNU gdb debugger\" Type=\"Executable\" BuildCmpWithGlobalSettings=\"append\" BuildLnkWithGlobalSettings=\"append\" BuildResWithGlobalSettings=\"append\">\n"
    r += "      <Compiler Options=\"-O2;-pedantic;-W;-std=c++14;-Wall;-Wextra;-Weffc++;-Werror;-fPIC\" C_Options=\"-O2;-Wall\" Assembler=\"\" Required=\"yes\" PreCompiledHeader=\"\" PCHInCommandLine=\"no\" PCHFlags=\"\" PCHFlagsPolicy=\"0\">\n"
    r += "        <IncludePath Value=\"../../src\"/>\n"
    r += "        <Preprocessor Value=\"NDEBUG\"/>\n"
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\" Required=\"yes\">\n"
    r += "        <Library Value=\"\"/>\n"
    r += "      </Linker>\n"
    r += "      <ResourceCompiler Options=\"\" Required=\"no\"/>\n"
    r += "      <General OutputFile=\"../../run/linux_x64_release/$(ProjectName)\" IntermediateDirectory=\"../../build/linux_x64_release\" Command=\"./$(ProjectName)\" CommandArguments=\"\" UseSeparateDebugArgs=\"no\" DebugArguments=\"\" WorkingDirectory=\"../../run/linux_x64_release/\" PauseExecWhenProcTerminates=\"yes\" IsGUIProgram=\"no\" IsEnabled=\"yes\"/>\n"
    r += "      <Environment EnvVarSetName=\"&lt;Use Defaults&gt;\" DbgSetName=\"&lt;Use Defaults&gt;\">\n"
    r += "        <![CDATA[]]>\n"
    r += "      </Environment>\n"
    r += "      <Debugger IsRemote=\"no\" RemoteHostName=\"\" RemoteHostPort=\"\" DebuggerPath=\"\" IsExtended=\"yes\">\n"
    r += "        <DebuggerSearchPaths/>\n"
    r += "        <PostConnectCommands/>\n"
    r += "        <StartupCommands/>\n"
    r += "      </Debugger>\n"
    r += "      <PreBuild/>\n"
    r += "      <PostBuild>\n"
    r += "        <Command Enabled=\"yes\">strip ../../run/linux_x64_release/$(ProjectName)</Command>\n"
    r += "      </PostBuild>\n"
    r += "      <CustomBuild Enabled=\"no\">\n"
    r += "        <RebuildCommand/>\n"
    r += "        <CleanCommand/>\n"
    r += "        <BuildCommand/>\n"
    r += "        <PreprocessFileCommand/>\n"
    r += "        <SingleFileCommand/>\n"
    r += "        <MakefileGenerationCommand/>\n"
    r += "        <ThirdPartyToolName>None</ThirdPartyToolName>\n"
    r += "        <WorkingDirectory/>\n"
    r += "      </CustomBuild>\n"
    r += "      <AdditionalRules>\n"
    r += "        <CustomPostBuild/>\n"
    r += "        <CustomPreBuild/>\n"
    r += "      </AdditionalRules>\n"
    r += "      <Completion EnableCpp11=\"no\" EnableCpp14=\"no\">\n"
    r += "        <ClangCmpFlagsC/>\n"
    r += "        <ClangCmpFlags/>\n"
    r += "        <ClangPP/>\n"
    r += "        <SearchPaths/>\n"
    r += "      </Completion>\n"
    r += "    </Configuration>\n"

    r += "    <Configuration Name=\"Release (LLVM)\" CompilerType=\"clang( tags/RELEASE_500/final )\" DebuggerType=\"LLDB Debugger\" Type=\"Executable\" BuildCmpWithGlobalSettings=\"append\" BuildLnkWithGlobalSettings=\"append\" BuildResWithGlobalSettings=\"append\">\n"
    r += "      <Compiler Options=\"-O2;-pedantic;-W;-std=c++14;-Wall;-Wextra;-Weffc++;-Werror;-fPIC\" C_Options=\"-O2;-Wall\" Assembler=\"\" Required=\"yes\" PreCompiledHeader=\"\" PCHInCommandLine=\"no\" PCHFlags=\"\" PCHFlagsPolicy=\"0\">\n"
    r += "        <IncludePath Value=\"../../src\"/>\n"
    r += "        <Preprocessor Value=\"NDEBUG\"/>\n"
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\" Required=\"yes\"/>\n"
    r += "      <ResourceCompiler Options=\"\" Required=\"no\"/>\n"
    r += "      <General OutputFile=\"../../run/linux_x64_release/$(ProjectName)\" IntermediateDirectory=\"../../build/linux_x64_release\" Command=\"./$(ProjectName)\" CommandArguments=\"\" UseSeparateDebugArgs=\"no\" DebugArguments=\"\" WorkingDirectory=\"../../run/linux_x64_release\" PauseExecWhenProcTerminates=\"yes\" IsGUIProgram=\"no\" IsEnabled=\"yes\"/>\n"
    r += "      <BuildSystem Name=\"Default\"/>\n"
    r += "      <Environment EnvVarSetName=\"&lt;Use Defaults&gt;\" DbgSetName=\"&lt;Use Defaults&gt;\">\n"
    r += "        <![CDATA[]]>\n"
    r += "      </Environment>\n"
    r += "      <Debugger IsRemote=\"no\" RemoteHostName=\"\" RemoteHostPort=\"\" DebuggerPath=\"\" IsExtended=\"no\">\n"
    r += "        <DebuggerSearchPaths/>\n"
    r += "        <PostConnectCommands/>\n"
    r += "        <StartupCommands/>\n"
    r += "      </Debugger>\n"
    r += "      <PreBuild/>\n"
    r += "      <PostBuild/>\n"
    r += "      <CustomBuild Enabled=\"no\">\n"
    r += "        <RebuildCommand/>\n"
    r += "        <CleanCommand/>\n"
    r += "        <BuildCommand/>\n"
    r += "        <PreprocessFileCommand/>\n"
    r += "        <SingleFileCommand/>\n"
    r += "        <MakefileGenerationCommand/>\n"
    r += "        <ThirdPartyToolName>None</ThirdPartyToolName>\n"
    r += "        <WorkingDirectory/>\n"
    r += "      </CustomBuild>\n"
    r += "      <AdditionalRules>\n"
    r += "        <CustomPostBuild/>\n"
    r += "        <CustomPreBuild/>\n"
    r += "      </AdditionalRules>\n"
    r += "      <Completion EnableCpp11=\"no\" EnableCpp14=\"no\">\n"
    r += "        <ClangCmpFlagsC/>\n"
    r += "        <ClangCmpFlags/>\n"
    r += "        <ClangPP/>\n"
    r += "        <SearchPaths/>\n"
    r += "      </Completion>\n"
    r += "    </Configuration>\n"

    r += "  </Settings>\n"
    r += "</CodeLite_Project>\n"
    return r

def msvc15slnfile_contents(project_name):
    r = "\xEF\xBB\xBF\n"
    r += "Microsoft Visual Studio Solution File, Format Version 12.00\n"
    r += "# Visual Studio 15\n"
    r += "VisualStudioVersion = 15.0.26228.9\n"
    r += "MinimumVisualStudioVersion = 10.0.40219.1\n"
    r += "Project(\"{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}\") = \"%s\", \"%s.vcxproj\", \"{7C79831C-A822-47F3-B80A-66BEB3F427A1}\"\n" % (project_name, project_name)
    r += "EndProject\n"
    r += "Global\n"
    r += "\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\n"
    r += "\t\tDebug|x64 = Debug|x64\n"
    r += "\t\tRelease|x64 = Release|x64\n"
    r += "\tEndGlobalSection\n"
    r += "\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\n"
    r += "\t\t{7C79831C-A822-47F3-B80A-66BEB3F427A1}.Debug|x64.ActiveCfg = Debug|x64\n"
    r += "\t\t{7C79831C-A822-47F3-B80A-66BEB3F427A1}.Debug|x64.Build.0 = Debug|x64\n"
    r += "\t\t{7C79831C-A822-47F3-B80A-66BEB3F427A1}.Release|x64.ActiveCfg = Release|x64\n"
    r += "\t\t{7C79831C-A822-47F3-B80A-66BEB3F427A1}.Release|x64.Build.0 = Release|x64\n"
    r += "\tEndGlobalSection\n"
    r += "\tGlobalSection(SolutionProperties) = preSolution\n"
    r += "\t\tHideSolutionNode = FALSE\n"
    r += "\tEndGlobalSection\n"
    r += "EndGlobal\n"
    return r

def msvc15projfile_contents(project_name):
    r = "\xEF\xBB\xBF<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
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
    r += "    <ProjectGuid>{7C79831C-A822-47F3-B80A-66BEB3F427A1}</ProjectGuid>\n"
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
    r += "      <WarningLevel>Level3</WarningLevel>\n"
    r += "      <Optimization>Disabled</Optimization>\n"
    r += "      <SDLCheck>true</SDLCheck>\n"
    r += "    </ClCompile>\n"
    r += "  </ItemDefinitionGroup>\n"
    r += "  <ItemDefinitionGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\">\n"
    r += "    <ClCompile>\n"
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
    #r += "  <ItemGroup>\n"
    #r += "    <ClInclude Include=\"..\\..\\include\\example.h\" />\n"
    #r += "  </ItemGroup>\n"
    r += "  <ItemGroup>\n"
    r += "    <ClCompile Include=\"..\\..\\src\\main.cpp\" />\n"
    r += "  </ItemGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />\n"
    r += "  <ImportGroup Label=\"ExtensionTargets\">\n"
    r += "  </ImportGroup>\n"
    r += "</Project>\n"
    return r

def mkfile_contents(project_name):
    r = ".PHONY : all prepfolders clean compile link\n\n"
    r += "APPNAME=%s\n\n" % project_name
    r += "BASE=../..\n"
    r += "BASE_SRC=$(BASE)/src\n"
    r += "BASE_OBJ=$(BASE)/build\n"
    r += "RUN=$(BASE)/run\n\n"
    r += "SRC=main.cpp\n\n"
    r += "COMPILER=g++\n\n"
    r += "ARCH := $(shell getconf LONG_BIT)\n"
    r += "CPPFLAGS=\n"
    r += "PLAT=generic\n\n"
    r += "ifeq ($(MODE),)\n"
    r += "\tMODE=debug\n"
    r += "endif\n\n"
    r += "UNAME_S := $(shell uname -s)\n"
    r += "ifeq ($(UNAME_S),Linux)\n"
    r += "\tCPPFLAGS += -D LINUX\n"
    r += "\tPLAT=linux\n"
    r += "endif\n"
    r += "ifeq ($(UNAME_S),Darwin)\n"
    r += "\tCPPFLAGS += -D OSX\n"
    r += "\tPLAT=macosx\n"
    r += "endif\n\n"
    r += "ifeq ($(MODE),debug)\n"
    r += "INTFLAGS = \\\n"
    r += "\t-g \\\n"
    r += "\t-Wall \\\n"
    r += "\t-Wextra \\\n"
    r += "\t-pedantic \\\n"
    r += "\t-Weffc++ \\\n"
    r += "\t-Werror \\\n"
    r += "\t-fPIC \\\n"
    r += "\t-D_GLIBCXX_DEBUG \\\n"
    r += "\t-std=c++14\n"
    r += "POSTBUILD=\n"
    r += "endif\n\n"
    r += "ifeq ($(MODE),release)\n"
    r += "INTFLAGS = \\\n"
    r += "\t-O2 \\\n"
    r += "\t-Wall \\\n"
    r += "\t-Wextra \\\n"
    r += "\t-pedantic \\\n"
    r += "\t-Weffc++ \\\n"
    r += "\t-Werror \\\n"
    r += "\t-fPIC \\\n"
    r += "\t-std=c++14\n"
    r += "POSTBUILD= strip $(FULL_APP_NAME)\n"
    r += "endif\n\n"
    r += "ifeq ($(ARCH),64)\n"
    r += "\tCPPFLAGS += $(INTFLAGS) -m64\n"
    r += "else\n"
    r += "CPPFLAGS += $(INTFLAGS)\n"
    r += "endif\n\n"
    r += "INCLUDES=-I$(BASE_SRC)\n"
    r += "LDFLAGS=\n\n"
    r += "BASE_OBJ_FULL=$(BASE_OBJ)/$(PLAT)_x$(ARCH)_$(MODE)\n"
    r += "RUN_FULL=$(RUN)/$(PLAT)_x$(ARCH)_$(MODE)\n"
    r += "ALL_OBJS=$(foreach src,$(SRC),$(BASE_OBJ_FULL)/$(notdir $(src:.cpp=.o)))\n"
    r += "FULL_APP_NAME=$(RUN_FULL)/$(APPNAME)\n\n"
    r += "all: prepfolders compile link\n\n"
    r += "prepfolders:\n"
    r += "\t@mkdir -p $(BASE_OBJ_FULL)\n"
    r += "\t@mkdir -p $(RUN_FULL)\n\n"
    r += "compile:\n"
    r += "\t$(foreach src,$(SRC),$(COMPILER) $(INCLUDES) $(CPPFLAGS) -c $(BASE_SRC)/$(src) -o $(BASE_OBJ_FULL)/$(notdir $(src:.cpp=.o));)\n\n"
    r += "link:\n"
    r += "\t$(COMPILER) -o $(FULL_APP_NAME) $(ALL_OBJS) $(LDFLAGS)\n"
    r += "\t$(POSTBUILD)\n\n"
    r += "clean:\n"
    r += "\t$(foreach objs,$(ALL_OBJS),rm -rf $(objs);)\n"
    r += "\trm -rf $(FULL_APP_NAME)\n"
    return r

def git_ign_contents(project_name):
    r = "*.swp\n"
    r += "*.o\n\n"
    r += "build\n"
    r += "run\n\n"
    r += "proj/codelite/%s.mk\n" % project_name
    r += "proj/codelite/%s.txt\n\n" % project_name
    r += "/proj/msvc15/.vs\n"
    r += "/proj/msvc15/%s.VC.db\n" % project_name
    r += "/proj/msvc15/%s.vcxproj.user\n\n" % project_name
    return r

def prjboot(target_dir, project_name):

    if not prjboot_validate(target_dir, project_name):
        sys.exit(1)

    prj_fullname_base = os.path.join(target_dir, project_name)
    base_prj = os.path.join(prj_fullname_base, "proj")

    base_build = os.path.join(prj_fullname_base, "build")
    base_build_linux_x64_debug = os.path.join(base_build, "linux_x64_debug")
    base_build_linux_x64_release = os.path.join(base_build, "linux_x64_release")
    base_build_windows_x64_debug = os.path.join(base_build, "windows_x64_debug")
    base_build_windows_x64_release = os.path.join(base_build, "windows_x64_release")

    base_run = os.path.join(prj_fullname_base, "run")
    base_run_linux_x64_debug = os.path.join(base_run, "linux_x64_debug")
    base_run_linux_x64_release = os.path.join(base_run, "linux_x64_release")
    base_run_windows_x64_debug = os.path.join(base_run, "windows_x64_debug")
    base_run_windows_x64_release = os.path.join(base_run, "windows_x64_release")

    base_src = os.path.join(prj_fullname_base, "src")

    base_git = os.path.join(prj_fullname_base, ".git")

    # basic structure
    os.mkdir(prj_fullname_base)
    os.mkdir(base_prj)

    os.mkdir(base_build)
    os.mkdir(base_build_linux_x64_debug)
    os.mkdir(base_build_linux_x64_release)
    os.mkdir(base_build_windows_x64_debug)
    os.mkdir(base_build_windows_x64_release)

    os.mkdir(base_run)
    os.mkdir(base_run_linux_x64_debug)
    os.mkdir(base_run_linux_x64_release)
    os.mkdir(base_run_windows_x64_debug)
    os.mkdir(base_run_windows_x64_release)

    os.mkdir(base_src)
    base_src_main_fn = os.path.join(base_src, "main.cpp")
    writecontents(base_src_main_fn, main_contents())

    base_prj_codelite = os.path.join(base_prj, "codelite")
    os.mkdir(base_prj_codelite)
    base_prj_codelite_fn = os.path.join(base_prj_codelite, "%s.project" % project_name)
    writecontents(base_prj_codelite_fn, codelite_projfile_contents(project_name))

    base_prj_msvc15 = os.path.join(base_prj, "msvc15")
    os.mkdir(base_prj_msvc15)
    base_prj_msvc15_sln = os.path.join(base_prj_msvc15, "%s.sln" % project_name)
    base_prj_msvc15_fn = os.path.join(base_prj_msvc15, "%s.vcxproj" % project_name)
    writecontents(base_prj_msvc15_sln, msvc15slnfile_contents(project_name))
    writecontents(base_prj_msvc15_fn, msvc15projfile_contents(project_name))

    base_prj_makefile = os.path.join(base_prj, "makefile")
    os.mkdir(base_prj_makefile)
    base_prj_makefile_fn = os.path.join(base_prj_makefile, "Makefile")
    writecontents(base_prj_makefile_fn, mkfile_contents(project_name))

    base_git_ign_fn = os.path.join(prj_fullname_base, ".gitignore")
    writecontents(base_git_ign_fn, git_ign_contents(project_name))

if __name__ == "__main__":

    td = os.getcwd()
    pn = "newproject"

    if len(sys.argv) == 2:
        td = sys.argv[1]
    if len(sys.argv) == 3:
        td = sys.argv[1]
        pn = sys.argv[2]

    prjboot(td, pn)
